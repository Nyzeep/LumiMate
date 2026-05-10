from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot

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


class ModelBridge(QObject):
    stateChanged = Signal()
    progressChanged = Signal()
    loadedChanged = Signal()
    logAdded = Signal(str)
    discoveryChanged = Signal()
    selectionChanged = Signal()

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

    @Slot()
    def loadSelectedModels(self) -> None:
        self._controller.load_models(self._config())

    @Slot()
    def switchSelectedModels(self) -> None:
        self._controller.switch_models(self._config())

    @Slot()
    def releaseCache(self) -> None:
        self._controller.release_cache()

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

    def _on_progress(self, step: int, total: int, message: str) -> None:
        self._progress_step = step
        self._progress_total = total
        self._progress_message = message
        self.progressChanged.emit()

    def _on_loaded(self, success: bool) -> None:
        self._loaded = success
        self.loadedChanged.emit()

    def _on_log_added(self, message: str) -> None:
        self._logs.append(message)
        self.logAdded.emit(message)
        self.discoveryChanged.emit()
