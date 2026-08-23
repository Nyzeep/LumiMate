from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from threading import RLock
from typing import Any

if __package__ in (None, ""):
    # 直接以脚本方式运行时把项目根加入 sys.path，保证白名单命令 python runtime/server.py --check 可用
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import Body, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import APP_AUTHOR, APP_PHILOSOPHY, APP_VERSION, PROJECT_ROOT, PROJECT_URL, UPDATE_MANIFEST_URL, AssistantConfig, UserSettings
from controllers import MainController
from services.model_catalog import MODEL_DOWNLOAD_CATALOG, directory_size_bytes, discover_model_directories
from services.model_download_service import ModelDownloadRequest, ModelDownloadService

VALID_AMBIENT_MODES = {"quiet", "breath", "stream"}
VALID_SCENES = {
    "home": 0,
    "chat": 0,
    "companion": 0,
    "workbench": 1,
    "loading": 1,
    "storage": 1,
    "settings": 2,
    "personality": 2,
    "about": 2,
}
DEFAULT_SCENES_BY_GROUP = {0: "home", 1: "workbench", 2: "settings"}

DEFAULT_CORS_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://tauri.localhost",
    "https://tauri.localhost",
    "tauri://localhost",
]



def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")

def _cors_origins() -> list[str]:
    raw = os.environ.get("LUMIMATE_CORS_ORIGINS", "").strip()
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return list(DEFAULT_CORS_ORIGINS)


def _normalize_scene(scene: str) -> str:
    scene = str(scene or "").strip()
    return scene if scene in VALID_SCENES else "home"


def _normalize_ambient_mode(mode: str) -> str:
    mode = str(mode or "quiet").strip().lower()
    return mode if mode in VALID_AMBIENT_MODES else "quiet"


def _format_bytes(value: int) -> str:
    size = float(max(0, value))
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    decimals = 0 if unit_index == 0 else 2
    return f"{size:.{decimals}f} {units[unit_index]}"


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self) -> None:
        self._loop = asyncio.get_running_loop()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        if not self._loop:
            return
        self._loop.call_soon_threadsafe(lambda: asyncio.create_task(self._broadcast({"type": event_type, **payload})))

    async def _broadcast(self, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for websocket in list(self._connections):
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)


class LumiRuntime:
    def __init__(self, publish: ConnectionManager):
        self._publish = publish
        self._lock = RLock()
        self.controller = MainController()
        self.settings = UserSettings.load()
        self.current_scene = _normalize_scene(self.settings.startup_page)
        self.current_scene_group = VALID_SCENES[self.current_scene]
        self.last_scene_by_group = dict(DEFAULT_SCENES_BY_GROUP)
        self.last_scene_by_group[self.current_scene_group] = self.current_scene
        self.defaults = AssistantConfig.defaults()

        self.runtime_state = "idle"
        self.runtime_message = "Lumi 正在静静地迎候你"
        self.progress_step = 0
        self.progress_total = 0
        self.progress_message = "静置"
        self.loaded = False
        self.logs: list[str] = []
        self.asr_models: list[str] = []
        self.llm_models: list[str] = []
        self.tts_models: list[str] = []
        self.selected_asr = self.defaults.asr_path
        self.selected_llm = self.defaults.llm_path
        self.selected_tts = self.defaults.tts_model_dir
        self.selected_ref_audio = self.defaults.ref_audio_path
        self.selected_ref_text = self.defaults.ref_text
        self.selected_tts_character = self.defaults.tts_character
        self.storage_items: list[dict[str, Any]] = []
        self.storage_used_bytes = 0
        self.storage_total_bytes = 0
        self.storage_free_bytes = 0
        self.download_service: ModelDownloadService | None = None
        self.download_state = "idle"
        self.download_progress = 0
        self.download_message = "等待选择模型星系。"
        self.download_logs: list[str] = []

        self.chat_ready = False
        self.chat_running = False
        self.chat_phase = "idle"
        self.chat_status = "由当前运行状态驱动的空间亮度与回应意愿。"
        self.voice_level = 0.0
        self.messages: list[dict[str, str]] = []

        self.mood = "quiet"
        self.breath_level = 0.52
        self.presence_level = 0.42
        self.is_listening = False
        self.stage_mode = "presence"
        self.speech_level = 0.0

        self._connect_controller()
        self.scan_models(emit=False)

    def _connect_controller(self) -> None:
        self.controller.state_changed.connect(self._on_state_changed)
        self.controller.progress.connect(self._on_progress)
        self.controller.loaded.connect(self._on_loaded)
        self.controller.log.connect(self._on_log_added)
        self.controller.user_text.connect(lambda text: self._append_message("user", "You", text))
        self.controller.assistant_text.connect(lambda text: self._append_message("assistant", "Lumi", text))
        self.controller.text_failed.connect(self._on_text_failed)
        self.controller.voice_level.connect(self._on_voice_level)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "boot": {"bridgeReady": True, "phase": "revealed", "ready": True},
                "app": {
                    "currentScene": self.current_scene,
                    "currentSceneGroup": self.current_scene_group,
                    "language": self.settings.language,
                    "startupPage": self.settings.startup_page,
                    "reduceMotion": self.settings.reduce_motion,
                    "checkUpdateOnStartup": self.settings.check_update_on_startup,
                    "ambientMode": _normalize_ambient_mode(self.settings.ambient_mode),
                    "appVersion": APP_VERSION,
                    "appAuthor": APP_AUTHOR,
                    "projectUrl": PROJECT_URL,
                    "authorAvatarUrl": "",
                    "updateSource": UPDATE_MANIFEST_URL or "Not configured",
                    "projectRoot": str(PROJECT_ROOT),
                    "pythonExecutable": sys.executable,
                },
                "runtime": {
                    "state": self.runtime_state,
                    "message": self.runtime_message,
                    "progressStep": self.progress_step,
                    "progressTotal": self.progress_total,
                    "progressMessage": self.progress_message,
                    "loaded": self.loaded,
                    "logs": self.logs[-12:],
                    "loadingSteps": self._loading_steps(),
                    "modelCatalog": self._model_catalog(),
                    "storageItems": self.storage_items,
                    "storageUsedLabel": _format_bytes(self.storage_used_bytes),
                    "storageTotalLabel": _format_bytes(self.storage_total_bytes),
                    "storageFreeLabel": _format_bytes(self.storage_free_bytes),
                    "storageUsageRatio": 0 if self.storage_total_bytes <= 0 else min(1.0, self.storage_used_bytes / self.storage_total_bytes),
                    "selectedAsr": self.selected_asr,
                    "selectedLlm": self.selected_llm,
                    "selectedTts": self.selected_tts,
                    "selectedRefAudio": self.selected_ref_audio,
                    "selectedRefText": self.selected_ref_text,
                    "selectedTtsCharacter": self.selected_tts_character,
                    "componentStatus": self._component_status(),
                    "downloadCatalog": MODEL_DOWNLOAD_CATALOG,
                    "downloadState": self.download_state,
                    "downloadProgress": self.download_progress,
                    "downloadMessage": self.download_message,
                    "downloadLogs": self.download_logs[-10:],
                },
                "chat": {
                    "ready": self.chat_ready,
                    "running": self.chat_running,
                    "status": self.chat_status,
                    "phase": self.chat_phase,
                    "voiceLevel": self.voice_level,
                    "messages": self.messages,
                },
                "emotion": {
                    "mood": self.mood,
                    "breathLevel": self.breath_level,
                    "presenceLevel": self.presence_level,
                    "isListening": self.is_listening,
                },
                "companion": {
                    "stageMode": self.stage_mode,
                    "speechLevel": self.speech_level,
                    "rendererType": "Portrait Stage",
                    "rendererCapability": "静态肖像、微光呼吸与声波脉冲",
                },
                "window": {"isFullscreen": False},
            }

    def emit_state(self, event_type: str = "state.patch", extra: dict[str, Any] | None = None) -> None:
        payload = {"state": self.snapshot()}
        if extra:
            payload.update(extra)
        self._publish.publish(event_type, payload)

    def frontend_ready(self) -> bool:
        self.emit_state("state.patch")
        return True

    def navigate(self, scene: str) -> bool:
        scene = _normalize_scene(scene)
        with self._lock:
            self.current_scene = scene
            self.current_scene_group = VALID_SCENES[scene]
            self.last_scene_by_group[self.current_scene_group] = scene
        self.emit_state()
        return True

    def set_scene_group(self, group_index: int) -> bool:
        group = max(0, min(2, int(group_index)))
        return self.navigate(self.last_scene_by_group.get(group, DEFAULT_SCENES_BY_GROUP[group]))

    def save_settings(self, payload: dict[str, Any]) -> bool:
        self.settings.language = str(payload.get("language") or self.settings.language)
        self.settings.check_update_on_startup = bool(payload.get("checkUpdateOnStartup", self.settings.check_update_on_startup))
        self.settings.startup_page = _normalize_scene(str(payload.get("startupPage") or self.settings.startup_page))
        self.settings.reduce_motion = bool(payload.get("reduceMotion", self.settings.reduce_motion))
        saved = self.settings.save()
        self.emit_state()
        return saved

    def set_ambient_mode(self, mode: str) -> bool:
        self.settings.ambient_mode = _normalize_ambient_mode(mode)
        saved = self.settings.save()
        self.emit_state()
        return saved

    def set_mood(self, mood: str) -> bool:
        self.mood = str(mood or "quiet")
        self.emit_state()
        return True

    def scan_models(self, emit: bool = True) -> bool:
        models_root = PROJECT_ROOT / "models"
        self.asr_models = discover_model_directories(models_root / "asr_model")
        self.llm_models = discover_model_directories(models_root / "llm_model")
        self.tts_models = discover_model_directories(models_root / "tts_model")
        if self.selected_asr not in self.asr_models and self.asr_models:
            self.selected_asr = self.asr_models[0]
        if self.selected_llm not in self.llm_models and self.llm_models:
            self.selected_llm = self.llm_models[0]
        if self.selected_tts not in self.tts_models and self.tts_models:
            self.selected_tts = self.tts_models[0]
        self._refresh_storage()
        if emit:
            self.emit_state()
        return True

    def scan_components(self) -> bool:
        self._set_download_state("scanning", "正在扫描本地模型组件...")
        self.scan_models(emit=False)
        if self.asr_models and self.llm_models:
            self._set_download_state("idle", "核心组件已经就位。")
        else:
            self._set_download_state("idle", "仍有核心组件等待下载。")
        self.emit_state()
        return True

    def open_model_galaxy(self) -> bool:
        self._set_download_state("idle", "已打开模型星系选择。")
        self.emit_state()
        return True

    def start_model_download(self, payload: dict[str, Any]) -> bool:
        kind = str(payload.get("kind") or "").strip().lower()
        provider = str(payload.get("provider") or "").strip().lower()
        model_id = str(payload.get("modelId") or payload.get("model_id") or "").strip()
        display_name = str(payload.get("displayName") or payload.get("display_name") or model_id).strip()

        if kind not in {"asr", "llm"}:
            self._set_download_state("failed", "这个模型类型暂时不能远程下载。")
            self.emit_state()
            return False
        if provider not in {"modelscope", "huggingface", "hf"}:
            self._set_download_state("failed", "请选择魔搭社区或 Hugging Face 下载路线。")
            self.emit_state()
            return False
        if not model_id:
            self._set_download_state("failed", "没有收到可下载的模型 ID。")
            self.emit_state()
            return False
        if self.download_service and self.download_service.is_alive():
            self._set_download_state("downloading", "已有模型正在下载，请等待当前任务完成。")
            self.emit_state()
            return False

        request = ModelDownloadRequest(
            kind=kind,
            provider="huggingface" if provider == "hf" else provider,
            model_id=model_id,
            display_name=display_name,
            target_root=PROJECT_ROOT / "models" / f"{kind}_model",
        )
        self.download_logs = []
        self.download_progress = 0
        self.download_service = ModelDownloadService(request)
        self.download_service.state_changed.connect(self._on_download_state_changed)
        self.download_service.progress_changed.connect(self._on_download_progress_changed)
        self.download_service.log_added.connect(self._on_download_log_added)
        self.download_service.finished_with_result.connect(self._on_download_finished)
        self._set_download_state("downloading", f"正在准备下载 {display_name}。")
        self.download_service.start()
        self.emit_state("download.progress")
        return True

    def cancel_model_download(self) -> bool:
        if not self.download_service or not self.download_service.is_alive():
            self._set_download_state("idle", "当前没有正在运行的下载任务。")
            self.emit_state()
            return False
        self.download_service.cancel()
        self._set_download_state("cancelled", "正在取消模型下载...")
        self.emit_state()
        return True

    def select_model(self, payload: dict[str, Any]) -> bool:
        model_type = str(payload.get("type") or payload.get("modelType") or "").strip()
        path = str(payload.get("path") or "").strip()
        if model_type == "asr":
            self.selected_asr = path
        elif model_type == "llm":
            self.selected_llm = path
        elif model_type == "tts":
            self.selected_tts = path
            self.selected_tts_character = Path(path).name if path else self.selected_tts_character
        self.emit_state()
        return True

    def open_path(self, payload: dict[str, Any]) -> bool:
        raw = str(payload.get("path") or "").strip()
        if not raw:
            return False
        target = Path(raw)
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
        try:
            if os.name == "nt":
                os.startfile(str(resolved))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(resolved)])
            else:
                subprocess.Popen(["xdg-open", str(resolved)])
            return True
        except OSError:
            return False

    def load_selected_models(self) -> bool:
        return bool(self.controller.load_models(self._config()))

    def switch_selected_models(self) -> bool:
        return bool(self.controller.switch_models(self._config()))

    def release_cache(self) -> bool:
        result = self.controller.release_cache()
        self.emit_state()
        return bool(result)

    def start_voice(self) -> bool:
        result = bool(self.controller.start_conversation())
        self.emit_state()
        return result

    def stop_voice(self) -> bool:
        self.controller.stop_conversation()
        self.chat_running = False
        self.chat_status = "空间回到安静。"
        self.emit_state()
        return True

    def send_text(self, text: str) -> bool:
        result = bool(self.controller.send_text(str(text or "")))
        self.emit_state()
        return result

    def clear_chat(self) -> bool:
        self.messages = []
        self.emit_state()
        return True

    def shutdown(self) -> None:
        self.controller.shutdown()

    def _config(self) -> AssistantConfig:
        return AssistantConfig(
            asr_path=self.selected_asr.strip(),
            llm_path=self.selected_llm.strip(),
            tts_model_dir=self.selected_tts.strip(),
            ref_audio_path=self.selected_ref_audio.strip(),
            ref_text=self.selected_ref_text.strip(),
            tts_character=self.selected_tts_character.strip() or Path(self.selected_tts).name or self.defaults.tts_character,
            max_new_tokens=100,
            chunk_sec=3,
            energy_threshold=0.005,
        )

    def _on_state_changed(self, state: str, message: str) -> None:
        with self._lock:
            self.runtime_state = state
            self.runtime_message = message
            self.chat_phase = state
            self.chat_status = message
            self.chat_ready = state in {"ready", "listening", "thinking", "replying"}
            self.chat_running = state == "listening"
            self._apply_emotion_for_state(state)
        self.emit_state("runtime.phase", {"phase": state})

    def _on_progress(self, step: int, total: int, message: str) -> None:
        with self._lock:
            self.progress_step = int(step)
            self.progress_total = int(total)
            self.progress_message = str(message)
        self.emit_state()

    def _on_loaded(self, success: bool) -> None:
        with self._lock:
            self.loaded = bool(success)
            self.chat_ready = bool(success)
            self.chat_status = "Ready." if success else "Load models to wake Lumi."
        self.emit_state()

    def _on_log_added(self, message: str) -> None:
        with self._lock:
            self.logs.append(str(message))
        self.emit_state("log.added", {"message": str(message)})

    def _on_text_failed(self, message: str) -> None:
        self.chat_status = str(message)
        self.emit_state()

    def _append_message(self, role: str, author: str, text: str) -> None:
        payload = {"role": role, "author": author, "body": str(text)}
        with self._lock:
            self.messages = [*self.messages, payload]
        self.emit_state("message.added", {"message": payload})

    def _on_voice_level(self, level: float) -> None:
        value = max(0.0, min(1.0, float(level)))
        self.voice_level = value
        self.speech_level = value
        self.emit_state()

    def _on_download_state_changed(self, state: str, message: str) -> None:
        self._set_download_state(state, message)
        self.emit_state("download.progress")

    def _on_download_progress_changed(self, progress: int, message: str) -> None:
        self.download_progress = max(0, min(100, int(progress)))
        if message:
            self.download_message = str(message)
        self.emit_state("download.progress")

    def _on_download_log_added(self, message: str) -> None:
        text = str(message or "").strip().replace(str(PROJECT_ROOT), "本地空间")
        if text:
            self.download_logs.append(text)
        self.emit_state("log.added", {"message": text})

    def _on_download_finished(self, success: bool, kind: str, path: str, message: str) -> None:
        if success and path:
            self.scan_models(emit=False)
            self.select_model({"type": kind, "path": path})
            self.download_progress = 100
            self._set_download_state("complete", "模型节点已经就位，可以返回核心舱唤醒 Lumi。")
        else:
            if self.download_state != "cancelled":
                self._set_download_state("failed", "模型下载没有完成，请切换来源或稍后重试。")
            if message:
                self.download_logs.append(str(message))
        self.download_service = None
        self.emit_state("download.progress")

    def _set_download_state(self, state: str, message: str) -> None:
        self.download_state = str(state)
        self.download_message = str(message)

    def _refresh_storage(self) -> None:
        targets = [
            ("storage.bucket.asr", PROJECT_ROOT / "models" / "asr_model"),
            ("storage.bucket.llm", PROJECT_ROOT / "models" / "llm_model"),
            ("storage.bucket.tts", PROJECT_ROOT / "models" / "tts_model"),
            ("storage.bucket.genie", PROJECT_ROOT / "GenieData"),
            ("storage.bucket.flash", PROJECT_ROOT / "预编译的flash atn"),
        ]
        usage = shutil.disk_usage(PROJECT_ROOT)
        self.storage_total_bytes = int(usage.total)
        self.storage_free_bytes = int(usage.free)
        self.storage_items = []
        tracked_total = 0
        for title_key, path in targets:
            size_bytes = directory_size_bytes(path)
            tracked_total += size_bytes
            self.storage_items.append(
                {
                    "titleKey": title_key,
                    "path": str(path),
                    "valueLabel": _format_bytes(size_bytes),
                    "sizeBytes": size_bytes,
                }
            )
        self.storage_used_bytes = tracked_total

    def _apply_emotion_for_state(self, state: str) -> None:
        self.is_listening = state == "listening"
        mapping = {
            "loading_asr": ("awakening", 0.70, 0.78, "awakening"),
            "loading_llm": ("awakening", 0.70, 0.78, "awakening"),
            "loading_tts": ("awakening", 0.70, 0.78, "awakening"),
            "switching": ("awakening", 0.70, 0.78, "awakening"),
            "validating": ("awakening", 0.70, 0.78, "awakening"),
            "listening": ("listening", 0.80, 0.88, "listening"),
            "thinking": ("thinking", 0.64, 0.74, "thinking"),
            "replying": ("replying", 0.72, 0.82, "replying"),
            "ready": ("present", 0.56, 0.62, "presence"),
            "failed": ("dim", 0.40, 0.28, "dim"),
        }
        mood, breath, presence, stage = mapping.get(state, ("quiet", 0.52, 0.42, "presence"))
        self.mood = mood
        self.breath_level = breath
        self.presence_level = presence
        self.stage_mode = stage

    def _loading_steps(self) -> list[dict[str, Any]]:
        current_step = max(
            self.progress_step,
            {
                "loading_asr": 1,
                "loading_llm": 2,
                "loading_tts": 4,
                "ready": 4,
                "listening": 4,
                "thinking": 4,
                "replying": 4,
            }.get(self.runtime_state, 0),
        )
        return [
            {"labelKey": "loading.step.asr", "done": self.loaded or current_step >= 1, "active": self.runtime_state == "loading_asr"},
            {"labelKey": "loading.step.llm", "done": self.loaded or current_step >= 2, "active": self.runtime_state == "loading_llm"},
            {"labelKey": "loading.step.tts", "done": self.loaded or current_step >= 3, "active": self.runtime_state == "loading_tts"},
            {"labelKey": "loading.step.reference", "done": self.loaded or current_step >= 4, "active": self.runtime_state == "loading_tts"},
        ]

    def _component_status(self) -> dict[str, Any]:
        return {
            "asr": self._build_component_status("asr", self.asr_models, self.selected_asr, "听觉节点"),
            "llm": self._build_component_status("llm", self.llm_models, self.selected_llm, "思维核心"),
            "tts": self._build_component_status(
                "tts",
                self.tts_models,
                self.selected_tts,
                "声线节点",
                placeholder=not bool(self.tts_models),
                note="TTS 远程下载暂未开放，后续将支持自行加载角色声线。",
            ),
            "ready": bool(self.asr_models and self.llm_models),
            "missingRequired": [kind for kind, items in (("asr", self.asr_models), ("llm", self.llm_models)) if not items],
        }

    def _model_catalog(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "asr": self._build_model_entries("asr", self.asr_models, self.selected_asr, "Listening Node", self.runtime_state == "loading_asr"),
            "llm": self._build_model_entries(
                "llm",
                self.llm_models,
                self.selected_llm,
                "Reasoning Core",
                self.runtime_state in {"loading_llm", "ready", "listening", "thinking", "replying"},
            ),
            "tts": self._build_model_entries("tts", self.tts_models, self.selected_tts, "Voice Node", self.runtime_state == "loading_tts" or self.loaded),
            "reference": [
                {
                    "id": f"reference:{self.selected_ref_audio or 'memory'}",
                    "title": self._friendly_title(self.selected_ref_audio) or "Reference Audio",
                    "subtitle": self.selected_ref_text or "Quiet memory sample",
                    "tags": ["Reference", "Memory"],
                    "status": "selected" if self.selected_ref_audio else "idle",
                    "selected": bool(self.selected_ref_audio),
                    "kind": "reference",
                    "path": self.selected_ref_audio,
                }
            ],
        }

    def _build_component_status(self, kind: str, items: list[str], selected_path: str, label: str, placeholder: bool = False, note: str = "") -> dict[str, Any]:
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

    def _build_model_entries(self, kind: str, items: list[str], selected_path: str, subtitle: str, runtime_active: bool) -> list[dict[str, Any]]:
        payload: list[dict[str, Any]] = []
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


def create_app(agent_service: Any | None = None) -> FastAPI:
    manager = ConnectionManager()
    runtime = LumiRuntime(manager)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        manager.bind_loop()
        try:
            yield
        finally:
            runtime.shutdown()

    app = FastAPI(title="LumiMate Runtime", version=APP_VERSION, lifespan=lifespan)
    app.state.runtime = runtime
    app.state.manager = manager
    app.state.agent_service = agent_service

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        return {"ok": True, "version": APP_VERSION}

    @app.get("/api/state")
    async def state() -> dict[str, Any]:
        return runtime.snapshot()

    def _agent_error(code: str, message: str) -> dict[str, Any]:
        return {"ok": False, "error": {"code": code, "message": message}}

    @app.post("/api/agent/status")
    async def agent_status() -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return {
                "ok": True,
                "ready": True,
                "harnessAvailable": False,
                "currentTask": None,
                "sessions": [],
            }
        return {"ok": True, **service.status()}

    @app.post("/api/agent/task/start")
    async def agent_task_start(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return _agent_error("AGENT_NOT_CONFIGURED", "Agent 子系统尚未配置")
        try:
            task = service.start_task(
                title=str(payload.get("title") or ""),
                goal=str(payload.get("goal") or ""),
                workspace=str(payload.get("workspace") or ""),
            )
        except ValueError as exc:
            return _agent_error("INVALID_WORKSPACE", str(exc))
        return {"ok": True, "task": task.to_api_dict()}

    @app.post("/api/agent/task/approve")
    async def agent_task_approve(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return _agent_error("AGENT_NOT_CONFIGURED", "Agent 子系统尚未配置")
        task_id = str(payload.get("taskId") or "")
        kind = str(payload.get("kind") or "plan")
        approve = _as_bool(payload.get("approve", False))
        if kind == "permission":
            try:
                task = service.approve_permission(
                    task_id,
                    request_id=str(payload.get("requestId") or ""),
                    grant_category=str(payload.get("grantCategory") or ""),
                    approve=_as_bool(payload.get("approve", False)),
                )
            except (KeyError, ValueError, RuntimeError) as exc:
                return _agent_error("INVALID_STATE", str(exc))
            return {"ok": True, "task": task.to_api_dict()}
        if kind != "plan":
            return _agent_error("INVALID_KIND", f"未知审批类型：{kind}")
        try:
            task = service.approve_plan(task_id, approve=approve)
        except (KeyError, ValueError, RuntimeError) as exc:
            return _agent_error("INVALID_STATE", str(exc))
        return {"ok": True, "task": task.to_api_dict()}

    @app.post("/api/agent/task/pause")
    async def agent_task_pause(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return _agent_error("AGENT_NOT_CONFIGURED", "Agent 子系统尚未配置")
        try:
            task = service.pause_task(str(payload.get("taskId") or ""))
        except (KeyError, ValueError, RuntimeError) as exc:
            return _agent_error("INVALID_STATE", str(exc))
        return {"ok": True, "task": task.to_api_dict()}

    @app.post("/api/agent/task/resume")
    async def agent_task_resume(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return _agent_error("AGENT_NOT_CONFIGURED", "Agent 子系统尚未配置")
        try:
            task = service.resume_task(str(payload.get("taskId") or ""))
        except (KeyError, ValueError, RuntimeError) as exc:
            return _agent_error("INVALID_STATE", str(exc))
        return {"ok": True, "task": task.to_api_dict()}

    @app.post("/api/agent/task/cancel")
    async def agent_task_cancel(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return _agent_error("AGENT_NOT_CONFIGURED", "Agent 子系统尚未配置")
        try:
            task = service.cancel_task(str(payload.get("taskId") or ""))
        except (KeyError, ValueError, RuntimeError) as exc:
            return _agent_error("INVALID_STATE", str(exc))
        return {"ok": True, "task": task.to_api_dict()}

    @app.post("/api/agent/session/list")
    async def agent_session_list() -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return {"ok": True, "sessions": []}
        return {"ok": True, "sessions": service.list_sessions()}

    @app.post("/api/agent/session/resume")
    async def agent_session_resume(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        service = app.state.agent_service
        if service is None:
            return _agent_error("AGENT_NOT_CONFIGURED", "Agent 子系统尚未配置")
        try:
            task = service.resume_session(
                session_id=str(payload.get("sessionId") or ""),
                title=str(payload.get("title") or "恢复任务"),
                goal=str(payload.get("goal") or ""),
                workspace=str(payload.get("workspace") or ""),
            )
        except ValueError as exc:
            return _agent_error("INVALID_WORKSPACE", str(exc))
        return {"ok": True, "task": task.to_api_dict()}
    @app.post("/api/shell/frontend-ready")
    async def frontend_ready() -> dict[str, Any]:
        return {"ok": runtime.frontend_ready()}

    @app.post("/api/app/navigate")
    async def navigate(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.navigate(str(payload.get("scene") or payload.get("page") or "home"))}

    @app.post("/api/app/scene-group")
    async def scene_group(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.set_scene_group(int(payload.get("groupIndex", 0)))}

    @app.post("/api/app/settings")
    async def settings(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.save_settings(payload)}

    @app.post("/api/app/ambient-mode")
    async def ambient_mode(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.set_ambient_mode(str(payload.get("mode") or "quiet"))}

    @app.post("/api/emotion/mood")
    async def mood(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.set_mood(str(payload.get("mood") or "quiet"))}

    @app.post("/api/model/load")
    async def model_load() -> dict[str, Any]:
        return {"ok": runtime.load_selected_models()}

    @app.post("/api/model/switch")
    async def model_switch() -> dict[str, Any]:
        return {"ok": runtime.switch_selected_models()}

    @app.post("/api/model/scan")
    async def model_scan() -> dict[str, Any]:
        return {"ok": runtime.scan_models()}

    @app.post("/api/model/scan-components")
    async def model_scan_components() -> dict[str, Any]:
        return {"ok": runtime.scan_components()}

    @app.post("/api/model/open-galaxy")
    async def model_open_galaxy() -> dict[str, Any]:
        return {"ok": runtime.open_model_galaxy()}

    @app.post("/api/model/release-cache")
    async def model_release_cache() -> dict[str, Any]:
        return {"ok": runtime.release_cache()}

    @app.post("/api/model/select")
    async def model_select(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.select_model(payload)}

    @app.post("/api/model/open-path")
    async def model_open_path(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.open_path(payload)}

    @app.post("/api/model/download/start")
    async def download_start(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.start_model_download(payload)}

    @app.post("/api/model/download/cancel")
    async def download_cancel() -> dict[str, Any]:
        return {"ok": runtime.cancel_model_download()}

    @app.post("/api/chat/start-voice")
    async def chat_start_voice() -> dict[str, Any]:
        return {"ok": runtime.start_voice()}

    @app.post("/api/chat/stop-voice")
    async def chat_stop_voice() -> dict[str, Any]:
        return {"ok": runtime.stop_voice()}

    @app.post("/api/chat/send-text")
    async def chat_send_text(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        return {"ok": runtime.send_text(str(payload.get("text") or ""))}

    @app.post("/api/chat/clear")
    async def chat_clear() -> dict[str, Any]:
        return {"ok": runtime.clear_chat()}

    @app.websocket("/ws/runtime")
    async def websocket_runtime(websocket: WebSocket) -> None:
        await manager.connect(websocket)
        try:
            await websocket.send_json({"type": "state.patch", "state": runtime.snapshot()})
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LumiMate Python Runtime")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    if args.check:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401

        print("LumiMate Python Runtime check passed.")
        return 0

    import uvicorn

    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="warning")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())




