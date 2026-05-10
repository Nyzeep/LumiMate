from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot


class CompanionBridge(QObject):
    stageModeChanged = Signal()
    speechLevelChanged = Signal()
    rendererChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stage_mode = "presence"
        self._speech_level = 0.0
        self._renderer_ready = False
        self._renderer_type = "adapter"
        self._renderer_capability = "Live2D / Spine placeholder"

    @Property(str, notify=stageModeChanged)
    def stageMode(self) -> str:
        return self._stage_mode

    @Property(float, notify=speechLevelChanged)
    def speechLevel(self) -> float:
        return self._speech_level

    @Property(bool, notify=rendererChanged)
    def rendererReady(self) -> bool:
        return self._renderer_ready

    @Property(str, notify=rendererChanged)
    def rendererType(self) -> str:
        return self._renderer_type

    @Property(str, notify=rendererChanged)
    def rendererCapability(self) -> str:
        return self._renderer_capability

    @Slot(str)
    def setStageMode(self, mode: str) -> None:
        mode = mode or "presence"
        if mode != self._stage_mode:
            self._stage_mode = mode
            self.stageModeChanged.emit()

    @Slot(float)
    def setSpeechLevel(self, level: float) -> None:
        level = max(0.0, min(1.0, float(level)))
        if level != self._speech_level:
            self._speech_level = level
            self.speechLevelChanged.emit()

    @Slot(bool, str, str)
    def setRendererState(self, ready: bool, renderer_type: str, capability: str) -> None:
        self._renderer_ready = bool(ready)
        self._renderer_type = renderer_type or "adapter"
        self._renderer_capability = capability or "Live2D / Spine placeholder"
        self.rendererChanged.emit()
