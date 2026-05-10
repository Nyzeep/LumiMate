from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot


class EmotionBridge(QObject):
    moodChanged = Signal()
    breathLevelChanged = Signal()
    presenceLevelChanged = Signal()
    listeningChanged = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._mood = "quiet"
        self._breath_level = 0.54
        self._presence_level = 0.42
        self._is_listening = False
        controller.state_changed.connect(self._on_state_changed)

    @Property(str, notify=moodChanged)
    def mood(self) -> str:
        return self._mood

    @Property(float, notify=breathLevelChanged)
    def breathLevel(self) -> float:
        return self._breath_level

    @Property(float, notify=presenceLevelChanged)
    def presenceLevel(self) -> float:
        return self._presence_level

    @Property(bool, notify=listeningChanged)
    def isListening(self) -> bool:
        return self._is_listening

    @Slot(str)
    def setMood(self, mood: str) -> None:
        self._set_mood(mood or "quiet")

    def _on_state_changed(self, state: str, message: str) -> None:
        del message
        self._is_listening = state == "listening"
        self.listeningChanged.emit()
        if state in {"loading_asr", "loading_llm", "loading_tts", "switching", "validating"}:
            self._set_mood("awakening")
            self._set_presence(0.78)
            self._set_breath(0.70)
        elif state == "listening":
            self._set_mood("listening")
            self._set_presence(0.88)
            self._set_breath(0.80)
        elif state == "thinking":
            self._set_mood("thinking")
            self._set_presence(0.74)
            self._set_breath(0.64)
        elif state == "replying":
            self._set_mood("replying")
            self._set_presence(0.82)
            self._set_breath(0.72)
        elif state == "ready":
            self._set_mood("present")
            self._set_presence(0.62)
            self._set_breath(0.56)
        elif state == "failed":
            self._set_mood("dim")
            self._set_presence(0.28)
            self._set_breath(0.40)
        else:
            self._set_mood("quiet")
            self._set_presence(0.42)
            self._set_breath(0.52)

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
