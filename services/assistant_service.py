from __future__ import annotations

import threading
import time

from PyQt6.QtCore import QMutex, QMutexLocker, QThread, pyqtSignal

from config import AssistantConfig


class AssistantService(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int, int, str)
    loaded = pyqtSignal(bool)
    state_changed = pyqtSignal(str, str)
    user_text = pyqtSignal(str)
    assistant_text = pyqtSignal(str)
    text_failed = pyqtSignal(str)

    def __init__(self, config: AssistantConfig):
        super().__init__()
        self.config = config
        self.assistant = None
        self.is_ready = False
        self.state = "idle"
        self._mutex = QMutex()
        self._text_thread: threading.Thread | None = None

    def set_state(self, state: str, message: str) -> None:
        self.state = state
        self.state_changed.emit(state, message)
        self.log.emit(message)

    def run(self) -> None:
        from core import VoiceAssistant

        try:
            self.set_state("validating", "正在准备模型加载。")
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
                self.set_state("ready", f"模型已就绪，用时 {elapsed:.1f} 秒。")
                self.loaded.emit(True)
            else:
                self.set_state("failed", "模型加载没有完成，请查看运行记录。")
                self.loaded.emit(False)

            while self.is_ready and not self.isInterruptionRequested():
                self.msleep(120)
        except Exception as exc:
            self.is_ready = False
            self.set_state("failed", f"模型启动失败：{exc}")
            self.loaded.emit(False)
        finally:
            if self.assistant:
                self.assistant.stop()
            if self.state not in {"failed", "idle"} and not self.is_ready:
                self.set_state("idle", "模型服务已停止。")

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
                self.log.emit("模型还没有准备好。")
                return False
            if self.assistant.running:
                self.state_changed.emit("running", "Lumi 已经在聆听。")
                return True
            started = self.assistant.start()
            if started:
                self.state_changed.emit("running", "Lumi 正在聆听。")
            return started

    def send_text(self, text: str) -> bool:
        text = text.strip()
        if not text:
            return False

        with QMutexLocker(self._mutex):
            if not self.assistant or not self.is_ready:
                message = "模型还没有准备好。"
                self.log.emit(message)
                self.text_failed.emit(message)
                return False
            if self._text_thread and self._text_thread.is_alive():
                message = "Lumi 正在组织上一段回应，请稍候。"
                self.log.emit(message)
                self.text_failed.emit(message)
                return False
            assistant = self.assistant

        def worker() -> None:
            try:
                self.log.emit("Lumi 正在组织回应。")
                assistant.respond_to_text(text, speak=True, emit_user=True)
            except Exception as exc:
                message = f"文字对话失败：{exc}"
                self.log.emit(message)
                self.text_failed.emit(message)

        self._text_thread = threading.Thread(target=worker, daemon=True)
        self._text_thread.start()
        return True

    def stop_conversation(self) -> None:
        with QMutexLocker(self._mutex):
            if self.assistant:
                self.state_changed.emit("stopping", "正在停止语音对话。")
                self.assistant.stop()
                if self.is_ready:
                    self.state_changed.emit("ready", "模型已就绪。")

    def shutdown(self) -> None:
        self.requestInterruption()
        self.stop_conversation()
        if self._text_thread and self._text_thread.is_alive():
            self._text_thread.join(timeout=1.0)
        self.wait(3500)
