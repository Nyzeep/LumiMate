from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot


class ChatBridge(QObject):
    readyChanged = Signal()
    runningChanged = Signal()
    statusChanged = Signal()
    messageAdded = Signal(str, str)
    clearRequested = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._ready = False
        self._running = False
        self._status = "Load models to wake Lumi."

        controller.state_changed.connect(self._on_state_changed)
        controller.loaded.connect(self._on_loaded)
        controller.user_text.connect(lambda text: self.messageAdded.emit("user", text))
        controller.assistant_text.connect(lambda text: self.messageAdded.emit("assistant", text))
        controller.text_failed.connect(self._on_text_failed)

    @Property(bool, notify=readyChanged)
    def ready(self) -> bool:
        return self._ready

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Slot(str)
    def sendText(self, text: str) -> None:
        text = text.strip()
        if not text:
            return
        if self._controller.send_text(text):
            self._set_status("Lumi is shaping a response.")

    @Slot()
    def startVoice(self) -> None:
        if self._controller.start_conversation():
            self._running = True
            self.runningChanged.emit()
            self._set_status("Listening.")

    @Slot()
    def stopVoice(self) -> None:
        self._controller.stop_conversation()
        self._running = False
        self.runningChanged.emit()
        self._set_status("Quiet again.")

    @Slot()
    def clear(self) -> None:
        self.clearRequested.emit()

    def _on_loaded(self, success: bool) -> None:
        self._ready = success
        self.readyChanged.emit()
        self._set_status("Ready." if success else "Load models to wake Lumi.")

    def _on_state_changed(self, state: str, message: str) -> None:
        ready = state in {"ready", "listening", "thinking", "replying"}
        running = state == "listening"
        if ready != self._ready:
            self._ready = ready
            self.readyChanged.emit()
        if running != self._running:
            self._running = running
            self.runningChanged.emit()
        self._set_status(message)

    def _on_text_failed(self, message: str) -> None:
        self._set_status(message)

    def _set_status(self, status: str) -> None:
        self._status = status
        self.statusChanged.emit()
