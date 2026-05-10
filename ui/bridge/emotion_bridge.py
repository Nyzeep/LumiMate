from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot


class EmotionBridge(QObject):
    moodChanged = pyqtSignal()
    breathLevelChanged = pyqtSignal()
    presenceLevelChanged = pyqtSignal()
    listeningChanged = pyqtSignal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._mood = "quiet"
        self._breath_level = 0.54
        self._presence_level = 0.42
        self._is_listening = False
        controller.state_changed.connect(self._on_state_changed)

    @pyqtProperty(str, notify=moodChanged)
    def mood(self) -> str:
        return self._mood

    @pyqtProperty(float, notify=breathLevelChanged)
    def breathLevel(self) -> float:
        return self._breath_level

    @pyqtProperty(float, notify=presenceLevelChanged)
    def presenceLevel(self) -> float:
        return self._presence_level

    @pyqtProperty(bool, notify=listeningChanged)
    def isListening(self) -> bool:
        return self._is_listening

    @pyqtSlot(str)
    def setMood(self, mood: str) -> None:
        self._set_mood(mood or "quiet")

    def _on_state_changed(self, state: str, message: str) -> None:
        self._is_listening = state == "running"
        self.listeningChanged.emit()
        if state in {"loading_asr", "loading_llm", "loading_tts", "switching"}:
            self._set_mood("awakening")
            self._set_presence(0.70)
            self._set_breath(0.68)
        elif state == "running":
            self._set_mood("listening")
            self._set_presence(0.86)
            self._set_breath(0.78)
        elif state == "ready":
            self._set_mood("present")
            self._set_presence(0.64)
            self._set_breath(0.58)
        elif state == "failed":
            self._set_mood("dim")
            self._set_presence(0.30)
            self._set_breath(0.42)
        else:
            self._set_mood("quiet")
            self._set_presence(0.42)
            self._set_breath(0.54)

    def _set_mood(self, mood: str) -> None:
        if mood != self._mood:
            self._mood = mood
            self.moodChanged.emit()

    def _set_breath(self, value: float) -> None:
        if value != self._breath_level:
            self._breath_level = value
            self.breathLevelChanged.emit()

    def _set_presence(self, value: float) -> None:
        if value != self._presence_level:
            self._presence_level = value
            self.presenceLevelChanged.emit()
