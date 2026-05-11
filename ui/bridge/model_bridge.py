from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from config import AssistantConfig, PROJECT_ROOT


def _discover_leaf_directories(root: Path) -> list[str]:
    if not root.exists():
        return []
    if any(root.iterdir()) and any(item.is_file() for item in root.iterdir()):
        return [str(root)]

    candidates: list[str] = []
    for child in sorted(root.iterdir(), key=lambda path: path.name.lower()):
        if not child.is_dir():
            continue
        if any(item.is_file() for item in child.iterdir()):
            candidates.append(str(child))
            continue
        for nested in sorted(child.rglob("*"), key=lambda path: path.name.lower()):
            if nested.is_dir() and any(item.is_file() for item in nested.iterdir()):
                candidates.append(str(nested))
    deduped: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def _directory_size_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    total = 0
    for file_path in root.rglob("*"):
        if file_path.is_file():
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
    return total


def _format_bytes(value: int) -> str:
    size = float(max(0, value))
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    decimals = 0 if unit_index == 0 else 2
    return f"{size:.{decimals}f} {units[unit_index]}"


class ModelBridge(QObject):
    stateChanged = Signal()
    progressChanged = Signal()
    loadedChanged = Signal()
    logAdded = Signal(str)
    discoveryChanged = Signal()
    selectionChanged = Signal()
    storageChanged = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._state = "idle"
        self._state_message = "Waiting"
        self._progress_step = 0
        self._progress_total = 0
        self._progress_message = "Waiting"
        self._loaded = False
        self._defaults = AssistantConfig.defaults()
        self._logs: list[str] = []
        self._asr_models: list[str] = []
        self._llm_models: list[str] = []
        self._tts_models: list[str] = []
        self._selected_asr = self._defaults.asr_path
        self._selected_llm = self._defaults.llm_path
        self._selected_tts = self._defaults.tts_model_dir
        self._selected_ref_audio = self._defaults.ref_audio_path
        self._selected_ref_text = self._defaults.ref_text
        self._selected_tts_character = self._defaults.tts_character
        self._storage_items: list[dict[str, object]] = []
        self._storage_used_bytes = 0
        self._storage_total_bytes = 0
        self._storage_free_bytes = 0

        controller.state_changed.connect(self._on_state_changed)
        controller.progress.connect(self._on_progress)
        controller.loaded.connect(self._on_loaded)
        controller.log.connect(self._on_log_added)

        self.scanModels()

    @Property(str, notify=stateChanged)
    def state(self) -> str:
        return self._state

    @Property(str, notify=stateChanged)
    def stateMessage(self) -> str:
        return self._state_message

    @Property(int, notify=progressChanged)
    def progressStep(self) -> int:
        return self._progress_step

    @Property(int, notify=progressChanged)
    def progressTotal(self) -> int:
        return self._progress_total

    @Property(str, notify=progressChanged)
    def progressMessage(self) -> str:
        return self._progress_message

    @Property(bool, notify=loadedChanged)
    def loaded(self) -> bool:
        return self._loaded

    @Property("QVariantList", notify=discoveryChanged)
    def asrModels(self):
        return self._asr_models

    @Property("QVariantList", notify=discoveryChanged)
    def llmModels(self):
        return self._llm_models

    @Property("QVariantList", notify=discoveryChanged)
    def ttsModels(self):
        return self._tts_models

    @Property("QVariantList", notify=discoveryChanged)
    def runtimeLog(self):
        return self._logs[-12:]

    @Property("QVariantList", notify=storageChanged)
    def storageItems(self):
        return self._storage_items

    @Property(str, notify=storageChanged)
    def storageUsedLabel(self) -> str:
        return _format_bytes(self._storage_used_bytes)

    @Property(str, notify=storageChanged)
    def storageTotalLabel(self) -> str:
        return _format_bytes(self._storage_total_bytes)

    @Property(str, notify=storageChanged)
    def storageFreeLabel(self) -> str:
        return _format_bytes(self._storage_free_bytes)

    @Property(float, notify=storageChanged)
    def storageUsageRatio(self) -> float:
        if self._storage_total_bytes <= 0:
            return 0.0
        return min(1.0, self._storage_used_bytes / self._storage_total_bytes)

    @Property("QVariantList", notify=progressChanged)
    def loadingSteps(self):
        current_step = max(
            self._progress_step,
            {
                "loading_asr": 1,
                "loading_llm": 2,
                "loading_tts": 4,
                "ready": 4,
                "listening": 4,
                "thinking": 4,
                "replying": 4,
            }.get(self._state, 0),
        )
        steps = [
            ("loading.step.asr", 1, "loading_asr"),
            ("loading.step.llm", 2, "loading_llm"),
            ("loading.step.tts", 3, "loading_tts"),
            ("loading.step.reference", 4, "loading_tts"),
        ]
        payload: list[dict[str, object]] = []
        for label_key, step_number, state_name in steps:
            payload.append(
                {
                    "labelKey": label_key,
                    "done": self._loaded or current_step >= step_number,
                    "active": self._state == state_name and current_step <= step_number,
                }
            )
        return payload

    @Property(str, notify=selectionChanged)
    def selectedAsr(self) -> str:
        return self._selected_asr

    @Property(str, notify=selectionChanged)
    def selectedLlm(self) -> str:
        return self._selected_llm

    @Property(str, notify=selectionChanged)
    def selectedTts(self) -> str:
        return self._selected_tts

    @Property(str, notify=selectionChanged)
    def selectedRefAudio(self) -> str:
        return self._selected_ref_audio

    @Property(str, notify=selectionChanged)
    def selectedRefText(self) -> str:
        return self._selected_ref_text

    @Property(str, notify=selectionChanged)
    def selectedTtsCharacter(self) -> str:
        return self._selected_tts_character

    @Property(str, constant=True)
    def modelRoot(self) -> str:
        return str(PROJECT_ROOT / "models")

    @Slot()
    def scanModels(self) -> None:
        models_root = PROJECT_ROOT / "models"
        self._asr_models = _discover_leaf_directories(models_root / "asr_model")
        self._llm_models = _discover_leaf_directories(models_root / "llm_model")
        self._tts_models = _discover_leaf_directories(models_root / "tts_model")

        if self._selected_asr not in self._asr_models and self._asr_models:
            self._selected_asr = self._asr_models[0]
        if self._selected_llm not in self._llm_models and self._llm_models:
            self._selected_llm = self._llm_models[0]
        if self._selected_tts not in self._tts_models and self._tts_models:
            self._selected_tts = self._tts_models[0]
        self._refresh_storage()
        self.discoveryChanged.emit()
        self.selectionChanged.emit()

    @Slot(str, str)
    def selectModel(self, model_type: str, path: str) -> None:
        path = path.strip()
        if model_type == "asr":
            self._selected_asr = path
        elif model_type == "llm":
            self._selected_llm = path
        elif model_type == "tts":
            self._selected_tts = path
            self._selected_tts_character = Path(path).name if path else self._selected_tts_character
        self.selectionChanged.emit()

    @Slot(str)
    def setReferenceAudio(self, path: str) -> None:
        self._selected_ref_audio = path.strip()
        self.selectionChanged.emit()

    @Slot(str)
    def setReferenceText(self, text: str) -> None:
        self._selected_ref_text = text
        self.selectionChanged.emit()

    @Slot(str)
    def setTtsCharacter(self, name: str) -> None:
        self._selected_tts_character = name.strip() or Path(self._selected_tts).name or self._defaults.tts_character
        self.selectionChanged.emit()

    @Slot(result=bool)
    def loadSelectedModels(self) -> bool:
        return bool(self._controller.load_models(self._config()))

    @Slot()
    def switchSelectedModels(self) -> None:
        self._controller.switch_models(self._config())

    @Slot()
    def releaseCache(self) -> None:
        self._controller.release_cache()

    @Slot(str, result=bool)
    def openPath(self, path: str) -> bool:
        path = (path or "").strip()
        if not path:
            return False
        target = Path(path)
        if not target.is_absolute():
            target = PROJECT_ROOT / target
        try:
            resolved = target.resolve()
            project_root = PROJECT_ROOT.resolve()
        except OSError:
            return False
        if not resolved.is_relative_to(project_root):
            return False
        if resolved.is_file():
            resolved = resolved.parent
        if not resolved.exists():
            return False
        return bool(QDesktopServices.openUrl(QUrl.fromLocalFile(str(resolved))))

    def _config(self) -> AssistantConfig:
        return AssistantConfig(
            asr_path=self._selected_asr.strip(),
            llm_path=self._selected_llm.strip(),
            tts_model_dir=self._selected_tts.strip(),
            ref_audio_path=self._selected_ref_audio.strip(),
            ref_text=self._selected_ref_text.strip(),
            tts_character=self._selected_tts_character.strip() or Path(self._selected_tts).name or self._defaults.tts_character,
            max_new_tokens=100,
            chunk_sec=3,
            energy_threshold=0.005,
        )

    def _on_state_changed(self, state: str, message: str) -> None:
        self._state = state
        self._state_message = message
        self.stateChanged.emit()
        self.progressChanged.emit()

    def _on_progress(self, step: int, total: int, message: str) -> None:
        self._progress_step = step
        self._progress_total = total
        self._progress_message = message
        self.progressChanged.emit()

    def _on_loaded(self, success: bool) -> None:
        self._loaded = success
        self.loadedChanged.emit()
        self.progressChanged.emit()

    def _on_log_added(self, message: str) -> None:
        self._logs.append(message)
        self.logAdded.emit(message)
        self.discoveryChanged.emit()

    def _refresh_storage(self) -> None:
        targets = [
            ("storage.bucket.asr", PROJECT_ROOT / "models" / "asr_model"),
            ("storage.bucket.llm", PROJECT_ROOT / "models" / "llm_model"),
            ("storage.bucket.tts", PROJECT_ROOT / "models" / "tts_model"),
            ("storage.bucket.genie", PROJECT_ROOT / "GenieData"),
            ("storage.bucket.flash", PROJECT_ROOT / "预编译的flash atn"),
        ]
        usage = shutil.disk_usage(PROJECT_ROOT)
        self._storage_total_bytes = int(usage.total)
        self._storage_free_bytes = int(usage.free)
        self._storage_items = []
        tracked_total = 0
        for title_key, path in targets:
            size_bytes = _directory_size_bytes(path)
            tracked_total += size_bytes
            self._storage_items.append(
                {
                    "titleKey": title_key,
                    "path": str(path),
                    "valueLabel": _format_bytes(size_bytes),
                    "sizeBytes": size_bytes,
                }
            )
        self._storage_used_bytes = tracked_total
        self.storageChanged.emit()
