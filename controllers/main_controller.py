from __future__ import annotations

import os

from PyQt6.QtCore import QObject, pyqtSignal

from config import AssistantConfig
from services import AssistantService


class MainController(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int, int, str)
    loaded = pyqtSignal(bool)
    state_changed = pyqtSignal(str, str)
    user_text = pyqtSignal(str)
    assistant_text = pyqtSignal(str)
    text_failed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.service: AssistantService | None = None
        self._loading = False

    def validate_config(self, config: AssistantConfig) -> list[str]:
        checks = {
            "ASR 模型": config.asr_path,
            "LLM 模型": config.llm_path,
            "TTS 目录": config.tts_model_dir,
            "参考音频": config.ref_audio_path,
        }
        return [f"{label} 不存在：{path}" for label, path in checks.items() if not os.path.exists(path)]

    def load_models(self, config: AssistantConfig) -> bool:
        if self.service and self.service.isRunning() and self._loading:
            self.log.emit("模型正在加载，请稍候。")
            return False

        issues = self.validate_config(config)
        if issues:
            for issue in issues:
                self.log.emit(issue)
            self.state_changed.emit("failed", "模型路径校验失败。")
            self.loaded.emit(False)
            return False

        if self.service and self.service.isRunning():
            self.service.shutdown()

        self._loading = True
        self.service = AssistantService(config)
        self.service.log.connect(self.log.emit)
        self.service.progress.connect(self.progress.emit)
        self.service.loaded.connect(self._on_loaded)
        self.service.state_changed.connect(self.state_changed.emit)
        self.service.user_text.connect(self.user_text.emit)
        self.service.assistant_text.connect(self.assistant_text.emit)
        self.service.text_failed.connect(self.text_failed.emit)
        self.state_changed.emit("validating", "正在校验模型路径。")
        self.service.start()
        return True

    def _on_loaded(self, success: bool) -> None:
        self._loading = False
        self.loaded.emit(success)

    def start_conversation(self) -> bool:
        if self.service:
            return self.service.start_conversation()
        self.log.emit("请先在工作台加载模型。")
        return False

    def send_text(self, text: str) -> bool:
        if self.service:
            return self.service.send_text(text)
        message = "请先在工作台加载模型。"
        self.log.emit(message)
        self.text_failed.emit(message)
        return False

    def stop_conversation(self) -> None:
        if self.service:
            self.service.stop_conversation()

    def shutdown(self) -> None:
        if self.service and self.service.isRunning():
            self.service.shutdown()
