from __future__ import annotations

import threading
import time

from config import AssistantConfig
from core.events import EventHook


class AssistantService:
    def __init__(self, config: AssistantConfig):
        self.config = config
        self.assistant = None
        self.is_ready = False
        self.state = "idle"
        self.log = EventHook()
        self.progress = EventHook()
        self.loaded = EventHook()
        self.state_changed = EventHook()
        self.user_text = EventHook()
        self.assistant_text = EventHook()
        self.text_failed = EventHook()
        self.voice_level = EventHook()
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._thread: threading.Thread | None = None
        self._text_thread: threading.Thread | None = None
        self._maintenance_thread: threading.Thread | None = None

    def start(self) -> None:
        if self.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="LumiAssistantService", daemon=True)
        self._thread.start()

    def is_alive(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def shutdown(self) -> None:
        self._stop_event.set()
        self.stop_conversation()
        if self._text_thread and self._text_thread.is_alive():
            self._text_thread.join(timeout=1.0)
        if self._maintenance_thread and self._maintenance_thread.is_alive():
            self._maintenance_thread.join(timeout=2.0)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.5)

    def set_state(self, state: str, message: str) -> None:
        self.state = state
        self.state_changed.emit(state, message)
        self.log.emit(message)

    def _run(self) -> None:
        from core import VoiceAssistant

        try:
            self.set_state("validating", "Preparing model load...")
            self.assistant = VoiceAssistant(
                self.config.to_core_dict(),
                on_user_text=self.user_text.emit,
                on_assistant_text=self.assistant_text.emit,
                on_log=self.log.emit,
                on_state=self.state_changed.emit,
                on_voice_level=self.voice_level.emit,
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

            while not self._stop_event.is_set():
                time.sleep(0.12)
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
        with self._lock:
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

        with self._lock:
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
                assistant.respond_to_text(text, speak=True, emit_user=True)
            except Exception as exc:
                message = f"Text conversation failed: {exc}"
                self.set_state("failed", message)
                self.text_failed.emit(message)

        self._text_thread = threading.Thread(target=worker, name="LumiTextResponse", daemon=True)
        self._text_thread.start()
        return True

    def switch_models(self, config: AssistantConfig) -> bool:
        with self._lock:
            if not self.assistant or not self.is_alive():
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

        self._maintenance_thread = threading.Thread(target=worker, name="LumiModelSwitch", daemon=True)
        self._maintenance_thread.start()
        return True

    def release_cache(self) -> bool:
        with self._lock:
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

        self._maintenance_thread = threading.Thread(target=worker, name="LumiCacheRelease", daemon=True)
        self._maintenance_thread.start()
        return True

    def stop_conversation(self) -> None:
        with self._lock:
            if self.assistant:
                self.assistant.stop()
                if self.is_ready:
                    self.state_changed.emit("ready", "Models are ready.")
