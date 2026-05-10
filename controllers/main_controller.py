from __future__ import annotations

import os

from PySide6.QtCore import QObject, Signal

from config import AssistantConfig, UPDATE_MANIFEST_URL
from core import IntegrityVerifier
from services import AssistantService
from services.update_service import UpdateService


class MainController(QObject):
    log = Signal(str)
    progress = Signal(int, int, str)
    loaded = Signal(bool)
    state_changed = Signal(str, str)
    user_text = Signal(str)
    assistant_text = Signal(str)
    text_failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.service: AssistantService | None = None
        self.update_service: UpdateService | None = None
        self._loading = False

    def validate_config(self, config: AssistantConfig) -> list[str]:
        checks = {
            "ASR model": config.asr_path,
            "LLM model": config.llm_path,
            "TTS directory": config.tts_model_dir,
            "Reference audio": config.ref_audio_path,
        }
        issues = [f"{label} does not exist: {path}" for label, path in checks.items() if not os.path.exists(path)]
        issues.extend(config.reference_audio().validate())
        return issues

    def validate_integrity(self) -> list[str]:
        return IntegrityVerifier().verify()

    def load_models(self, config: AssistantConfig) -> bool:
        if self.service and self.service.isRunning() and self._loading:
            self.log.emit("Models are already loading. Please wait.")
            return False

        if not self._validate_before_model_action(config):
            return False

        if self.service and self.service.isRunning():
            self.service.shutdown()

        self._loading = True
        self.service = AssistantService(config)
        self._connect_service(self.service)
        self.state_changed.emit("validating", "Validating model paths...")
        self.service.start()
        return True

    def switch_models(self, config: AssistantConfig) -> bool:
        if not self.service or not self.service.isRunning():
            return self.load_models(config)
        if not self._validate_before_model_action(config):
            return False
        self.state_changed.emit("switching", "Switching models...")
        return self.service.switch_models(config)

    def release_cache(self) -> bool:
        if self.service and self.service.isRunning():
            return self.service.release_cache()
        self.state_changed.emit("releasing_cache", "Releasing cache and VRAM...")
        self.log.emit("No active model service. Runtime cache release requested.")
        return True

    def check_updates(self) -> bool:
        if self.update_service and self.update_service.isRunning():
            self.log.emit("Update check is already running.")
            return False
        self.update_service = UpdateService(UPDATE_MANIFEST_URL)
        self.update_service.progress.connect(self.log.emit)
        self.update_service.progress.connect(lambda message: self.state_changed.emit("checking_update", message))
        self.update_service.finished.connect(self._on_update_finished)
        self.state_changed.emit("checking_update", "Checking updates...")
        self.update_service.start()
        return True

    def _validate_before_model_action(self, config: AssistantConfig) -> bool:
        integrity_issues = self.validate_integrity()
        if integrity_issues:
            for issue in integrity_issues:
                self.log.emit(issue)
            self.state_changed.emit("failed", "Project integrity validation failed.")
            self.loaded.emit(False)
            return False

        issues = self.validate_config(config)
        if issues:
            for issue in issues:
                self.log.emit(issue)
            self.state_changed.emit("failed", "Model path validation failed.")
            self.loaded.emit(False)
            return False
        return True

    def _connect_service(self, service: AssistantService) -> None:
        service.log.connect(self.log.emit)
        service.progress.connect(self.progress.emit)
        service.loaded.connect(self._on_loaded)
        service.state_changed.connect(self.state_changed.emit)
        service.user_text.connect(self.user_text.emit)
        service.assistant_text.connect(self.assistant_text.emit)
        service.text_failed.connect(self.text_failed.emit)

    def _on_loaded(self, success: bool) -> None:
        self._loading = False
        self.loaded.emit(success)

    def _on_update_finished(self, success: bool, message: str) -> None:
        self.log.emit(message)
        self.state_changed.emit("ready" if success else "idle", message)

    def start_conversation(self) -> bool:
        if self.service:
            return self.service.start_conversation()
        self.log.emit("Load models in the workbench first.")
        return False

    def send_text(self, text: str) -> bool:
        if self.service:
            return self.service.send_text(text)
        message = "Load models in the workbench first."
        self.log.emit(message)
        self.text_failed.emit(message)
        return False

    def stop_conversation(self) -> None:
        if self.service:
            self.service.stop_conversation()

    def shutdown(self) -> None:
        if self.update_service and self.update_service.isRunning():
            self.update_service.requestInterruption()
            self.update_service.wait(1500)
        if self.service and self.service.isRunning():
            self.service.shutdown()
