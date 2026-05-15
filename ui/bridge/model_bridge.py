from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from config import AssistantConfig, PROJECT_ROOT
from services.model_download_service import ModelDownloadRequest, ModelDownloadService


MODEL_DOWNLOAD_CATALOG: dict[str, list[dict[str, object]]] = {
    "asr": [
        {
            "id": "qwen3-asr-flash",
            "title": "Qwen3 ASR Flash",
            "subtitle": "轻量听觉节点，适合作为 Lumi 的默认耳朵。",
            "sizeLabel": "约 5 GB",
            "providers": {
                "modelscope": "Qwen/Qwen3-ASR-Flash",
                "huggingface": "Qwen/Qwen3-ASR-Flash",
            },
        },
        {
            "id": "qwen2-audio-7b",
            "title": "Qwen2 Audio 7B",
            "subtitle": "更完整的音频理解节点，下载和运行成本更高。",
            "sizeLabel": "约 15 GB",
            "providers": {
                "modelscope": "qwen/Qwen2-Audio-7B-Instruct",
                "huggingface": "Qwen/Qwen2-Audio-7B-Instruct",
            },
        },
    ],
    "llm": [
        {
            "id": "qwen2-5-0-5b-instruct",
            "title": "Qwen2.5 0.5B Instruct",
            "subtitle": "小体量思维核心，适合先让 Lumi 轻盈醒来。",
            "sizeLabel": "约 1 GB",
            "providers": {
                "modelscope": "qwen/Qwen2.5-0.5B-Instruct",
                "huggingface": "Qwen/Qwen2.5-0.5B-Instruct",
            },
        },
        {
            "id": "qwen2-5-1-5b-instruct",
            "title": "Qwen2.5 1.5B Instruct",
            "subtitle": "更稳的本地对话核心，需要更多显存与磁盘空间。",
            "sizeLabel": "约 3 GB",
            "providers": {
                "modelscope": "qwen/Qwen2.5-1.5B-Instruct",
                "huggingface": "Qwen/Qwen2.5-1.5B-Instruct",
            },
        },
    ],
    "tts": [
        {
            "id": "tts-placeholder",
            "title": "声线星系预留",
            "subtitle": "TTS 将在后续版本支持用户自行加载角色声线模型。",
            "sizeLabel": "稍后开放",
            "providers": {},
            "placeholder": True,
        }
    ],
}


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
    componentStatusChanged = Signal()
    downloadCatalogChanged = Signal()
    downloadStateChanged = Signal()
    downloadProgressChanged = Signal()
    downloadLogAdded = Signal(str)

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
        self._download_service: ModelDownloadService | None = None
        self._download_state = "idle"
        self._download_progress = 0
        self._download_message = "等待选择模型星系。"
        self._download_logs: list[str] = []

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

    @Property("QVariantMap", notify=componentStatusChanged)
    def componentStatus(self):
        return {
            "asr": self._build_component_status("asr", self._asr_models, self._selected_asr, "听觉节点"),
            "llm": self._build_component_status("llm", self._llm_models, self._selected_llm, "思维核心"),
            "tts": self._build_component_status(
                "tts",
                self._tts_models,
                self._selected_tts,
                "声线节点",
                placeholder=not bool(self._tts_models),
                note="TTS 远程下载暂未开放，后续将支持自行加载角色声线。",
            ),
            "ready": bool(self._asr_models and self._llm_models),
            "missingRequired": [kind for kind, items in (("asr", self._asr_models), ("llm", self._llm_models)) if not items],
        }

    @Property("QVariantMap", notify=downloadCatalogChanged)
    def downloadCatalog(self):
        return MODEL_DOWNLOAD_CATALOG

    @Property(str, notify=downloadStateChanged)
    def downloadState(self) -> str:
        return self._download_state

    @Property(int, notify=downloadProgressChanged)
    def downloadProgress(self) -> int:
        return self._download_progress

    @Property(str, notify=downloadStateChanged)
    def downloadMessage(self) -> str:
        return self._download_message

    @Property("QVariantList", notify=downloadStateChanged)
    def downloadLogs(self):
        return self._download_logs[-10:]

    @Property("QVariantMap", notify=selectionChanged)
    def modelCatalog(self):
        return {
            "asr": self._build_model_entries(
                "asr",
                self._asr_models,
                self._selected_asr,
                "Listening Node",
                self._state == "loading_asr",
            ),
            "llm": self._build_model_entries(
                "llm",
                self._llm_models,
                self._selected_llm,
                "Reasoning Core",
                self._state in {"loading_llm", "ready", "listening", "thinking", "replying"},
            ),
            "tts": self._build_model_entries(
                "tts",
                self._tts_models,
                self._selected_tts,
                "Voice Node",
                self._state == "loading_tts" or self._loaded,
            ),
            "reference": [
                {
                    "id": f"reference:{self._selected_ref_audio or 'memory'}",
                    "title": self._friendly_title(self._selected_ref_audio) or "Reference Audio",
                    "subtitle": self._selected_ref_text or "Quiet memory sample",
                    "tags": ["Reference", "Memory"],
                    "status": "selected" if self._selected_ref_audio else "idle",
                    "selected": bool(self._selected_ref_audio),
                    "kind": "reference",
                    "path": self._selected_ref_audio,
                }
            ],
        }

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
        self.componentStatusChanged.emit()

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
        self.componentStatusChanged.emit()

    @Slot()
    def scanComponents(self) -> None:
        self._set_download_state("scanning", "正在扫描本地模型组件...")
        self.scanModels()
        if self._asr_models and self._llm_models:
            self._set_download_state("idle", "核心组件已经就位。")
        else:
            self._set_download_state("idle", "仍有核心组件等待下载。")

    @Slot()
    def openModelGalaxy(self) -> None:
        self._set_download_state("idle", "已打开模型星系选择。")

    @Slot(str, str, str, str, result=bool)
    def startModelDownload(self, kind: str, provider: str, model_id: str, display_name: str) -> bool:
        kind = (kind or "").strip().lower()
        provider = (provider or "").strip().lower()
        model_id = (model_id or "").strip()
        display_name = (display_name or "").strip() or model_id

        if kind not in {"asr", "llm"}:
            self._set_download_state("failed", "这个模型类型暂时不能远程下载。")
            return False
        if provider not in {"modelscope", "huggingface", "hf"}:
            self._set_download_state("failed", "请选择魔搭社区或 Hugging Face 下载路线。")
            return False
        if not model_id:
            self._set_download_state("failed", "没有收到可下载的模型 ID。")
            return False
        if self._download_service and self._download_service.isRunning():
            self._set_download_state("downloading", "已有模型正在下载，请等待当前任务完成。")
            return False

        target_root = PROJECT_ROOT / "models" / f"{kind}_model"
        request = ModelDownloadRequest(
            kind=kind,
            provider="huggingface" if provider == "hf" else provider,
            model_id=model_id,
            display_name=display_name,
            target_root=target_root,
        )
        self._download_logs = []
        self._download_progress = 0
        self._download_service = ModelDownloadService(request, self)
        self._download_service.state_changed.connect(self._on_download_state_changed)
        self._download_service.progress_changed.connect(self._on_download_progress_changed)
        self._download_service.log_added.connect(self._on_download_log_added)
        self._download_service.finished_with_result.connect(self._on_download_finished)
        self._set_download_state("downloading", f"正在准备下载 {display_name}。")
        self.downloadProgressChanged.emit()
        self._download_service.start()
        return True

    @Slot(result=bool)
    def cancelModelDownload(self) -> bool:
        if not self._download_service or not self._download_service.isRunning():
            self._set_download_state("idle", "当前没有正在运行的下载任务。")
            return False
        self._download_service.cancel()
        self._set_download_state("cancelled", "正在取消模型下载...")
        return True

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

    def _on_download_state_changed(self, state: str, message: str) -> None:
        self._set_download_state(state, message)

    def _on_download_progress_changed(self, progress: int, message: str) -> None:
        self._download_progress = max(0, min(100, int(progress)))
        if message:
            self._download_message = message
        self.downloadProgressChanged.emit()
        self.downloadStateChanged.emit()

    def _on_download_log_added(self, message: str) -> None:
        self._download_logs.append(self._soften_download_log(message))
        self.downloadLogAdded.emit(message)
        self.downloadStateChanged.emit()

    def _on_download_finished(self, success: bool, kind: str, path: str, message: str) -> None:
        if success and path:
            self.scanModels()
            self.selectModel(kind, path)
            self._download_progress = 100
            self._set_download_state("complete", "模型节点已经就位，可以返回核心舱唤醒 Lumi。")
        else:
            if self._download_state != "cancelled":
                self._set_download_state("failed", "模型下载没有完成，请切换来源或稍后重试。")
            self._on_download_log_added(message)
        self._download_service = None
        self.downloadProgressChanged.emit()

    def _set_download_state(self, state: str, message: str) -> None:
        self._download_state = state
        self._download_message = message
        self.downloadStateChanged.emit()

    def _soften_download_log(self, message: str) -> str:
        text = str(message or "").strip()
        if not text:
            return ""
        return text.replace(str(PROJECT_ROOT), "本地空间")

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

    def _build_component_status(
        self,
        kind: str,
        items: list[str],
        selected_path: str,
        label: str,
        placeholder: bool = False,
        note: str = "",
    ) -> dict[str, object]:
        count = len(items)
        ready = count > 0
        return {
            "kind": kind,
            "label": label,
            "ready": ready,
            "count": count,
            "selected": selected_path if ready else "",
            "selectedName": self._friendly_title(selected_path) if ready else "",
            "status": "ready" if ready else "placeholder" if placeholder else "missing",
            "note": note or ("已检测到本地模型。" if ready else "等待下载或导入模型。"),
        }

    def _build_model_entries(
        self,
        kind: str,
        items: list[str],
        selected_path: str,
        subtitle: str,
        runtime_active: bool,
    ) -> list[dict[str, object]]:
        payload: list[dict[str, object]] = []
        for path in items:
            is_selected = path == selected_path
            status = "active" if runtime_active and is_selected else "selected" if is_selected else "ready"
            tags = [kind.upper()]
            if is_selected:
                tags.append("Selected")
            if runtime_active and is_selected:
                tags.append("Active")
            payload.append(
                {
                    "id": f"{kind}:{path}",
                    "title": self._friendly_title(path),
                    "subtitle": subtitle,
                    "tags": tags,
                    "status": status,
                    "selected": is_selected,
                    "kind": kind,
                    "path": path,
                }
            )
        if payload:
            return payload
        return [
            {
                "id": f"{kind}:empty",
                "title": "No node detected",
                "subtitle": subtitle,
                "tags": [kind.upper(), "Empty"],
                "status": "empty",
                "selected": False,
                "kind": kind,
                "path": "",
            }
        ]

    def _friendly_title(self, path: str) -> str:
        if not path:
            return ""
        name = Path(path).name or Path(path).stem
        return name.replace("_", " ").replace("-", " ").strip() or name
