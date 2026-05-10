from __future__ import annotations

import threading
import time

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

from config import AssistantConfig


class AssistantService(QThread):
    log = Signal(str)
    progress = Signal(int, int, str)
    loaded = Signal(bool)
    state_changed = Signal(str, str)
    user_text = Signal(str)
    assistant_text = Signal(str)
    text_failed = Signal(str)

    def __init__(self, config: AssistantConfig):
        super().__init__()
        self.config = config
        self.assistant = None
        self.is_ready = False
        self.state = "idle"
        self._mutex = QMutex()
        self._text_thread: threading.Thread | None = None
        self._maintenance_thread: threading.Thread | None = None

    def set_state(self, state: str, message: str) -> None:
        self.state = state
        self.state_changed.emit(state, message)
        self.log.emit(message)

    def run(self) -> None:
        from core import VoiceAssistant

        try:
            self.set_state("validating", "Preparing model load...")
            self.assistant = VoiceAssistant(
                self.config.to_core_dict(),
                on_user_text=self.user_text.emit,
                on_assistant_text=self.assistant_text.emit,
                on_log=self.log.emit,
                on_state=self.state_changed.emit,
            )
            start = time.perf_counter()
            self.is_ready = self.assistant.load_models(progress_callback=self._progress)
            if self.is_ready:
                elapsed = time.perf_counter() - start
                self.set_state("ready", f"Models ready in {elapsed:.1f}s.")
                self.loaded.emit(True)
            else:
                self.set_state("failed", "Model loading did not complete. Check the runtime log.")
                self.loaded.emit(False)

            while not self.isInterruptionRequested():
                self.msleep(120)
        except Exception as exc:
            self.is_ready = False
            self.set_state("failed", f"Model service failed: {exc}")
            self.loaded.emit(False)
        finally:
            if self.assistant:
                self.assistant.release_models()
            self.is_ready = False
            if self.state not in {"failed", "idle"}:
                self.set_state("idle", "Model service stopped.")

    def _progress(self, step: int, total: int, message: str) -> None:
        self.progress.emit(step, total, message)
        stage = {
            1: "loading_asr",
            2: "loading_llm",
            3: "loading_tts",
            4: "loading_tts",
        }.get(step, "validating")
        self.state_changed.emit(stage, message)

    def start_conversation(self) -> bool:
        with QMutexLocker(self._mutex):
            if not self.assistant or not self.is_ready:
                self.log.emit("Models are not ready.")
                return False
            if self.assistant.running:
                self.state_changed.emit("listening", "Lumi is already listening.")
                return True
            started = self.assistant.start()
            if started:
                self.state_changed.emit("listening", "Lumi is listening.")
            return started

    def send_text(self, text: str) -> bool:
        text = text.strip()
        if not text:
            return False

        with QMutexLocker(self._mutex):
            if not self.assistant or not self.is_ready:
                message = "Models are not ready."
                self.log.emit(message)
                self.text_failed.emit(message)
                return False
            if self._text_thread and self._text_thread.is_alive():
                message = "Lumi is still responding. Please wait."
                self.log.emit(message)
                self.text_failed.emit(message)
                return False
            assistant = self.assistant

        def worker() -> None:
            try:
                self.state_changed.emit("thinking", "Lumi is composing a response.")
                self.log.emit("Lumi is composing a response...")
                assistant.respond_to_text(text, speak=True, emit_user=True)
                self.state_changed.emit("replying", "Lumi is shaping a response.")
                self.state_changed.emit("ready", "Lumi is present.")
            except Exception as exc:
                message = f"Text conversation failed: {exc}"
                self.log.emit(message)
                self.text_failed.emit(message)
                self.state_changed.emit("failed", message)

        self._text_thread = threading.Thread(target=worker, daemon=True)
        self._text_thread.start()
        return True

    def switch_models(self, config: AssistantConfig) -> bool:
        with QMutexLocker(self._mutex):
            if not self.assistant or not self.isRunning():
                self.log.emit("Start the model service before switching models.")
                return False
            if self._maintenance_thread and self._maintenance_thread.is_alive():
                self.log.emit("A maintenance task is already running.")
                return False
            assistant = self.assistant

        def worker() -> None:
            try:
                self.set_state("switching", "Switching models...")
                self.is_ready = False
                assistant.stop()
                success = assistant.switch_models(config.to_core_dict(), progress_callback=self._progress)
                self.config = config
                self.is_ready = success
                if success:
                    self.set_state("ready", "Models switched and ready.")
                else:
                    self.set_state("failed", "Model switch failed.")
                self.loaded.emit(success)
            except Exception as exc:
                self.is_ready = False
                self.set_state("failed", f"Model switch failed: {exc}")
                self.loaded.emit(False)

        self._maintenance_thread = threading.Thread(target=worker, daemon=True)
        self._maintenance_thread.start()
        return True

    def release_cache(self) -> bool:
        with QMutexLocker(self._mutex):
            if self._maintenance_thread and self._maintenance_thread.is_alive():
                self.log.emit("A maintenance task is already running.")
                return False
            assistant = self.assistant

        def worker() -> None:
            try:
                self.set_state("releasing_cache", "Releasing cache and VRAM...")
                if assistant:
                    assistant.release_cache()
                else:
                    from services.model_manager import ModelManager

                    ModelManager(self.log.emit).clear_cache()
                self.set_state("ready" if self.is_ready else "idle", "Cache released.")
            except Exception as exc:
                self.set_state("failed", f"Cache release failed: {exc}")

        self._maintenance_thread = threading.Thread(target=worker, daemon=True)
        self._maintenance_thread.start()
        return True

    def stop_conversation(self) -> None:
        with QMutexLocker(self._mutex):
            if self.assistant:
                self.state_changed.emit("present", "Stopping voice conversation...")
                self.assistant.stop()
                if self.is_ready:
                    self.state_changed.emit("ready", "Models are ready.")

    def shutdown(self) -> None:
        self.requestInterruption()
        self.stop_conversation()
        if self._text_thread and self._text_thread.is_alive():
            self._text_thread.join(timeout=1.0)
        if self._maintenance_thread and self._maintenance_thread.is_alive():
            self._maintenance_thread.join(timeout=2.0)
        self.wait(3500)
