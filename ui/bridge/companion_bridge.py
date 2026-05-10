from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot


class CompanionBridge(QObject):
    stageModeChanged = pyqtSignal()
    speechLevelChanged = pyqtSignal()
    live2dReadyChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stage_mode = "presence"
        self._speech_level = 0.0
        self._live2d_ready = False

    @pyqtProperty(str, notify=stageModeChanged)
    def stageMode(self) -> str:
        return self._stage_mode

    @pyqtProperty(float, notify=speechLevelChanged)
    def speechLevel(self) -> float:
        return self._speech_level

    @pyqtProperty(bool, notify=live2dReadyChanged)
    def live2dReady(self) -> bool:
        return self._live2d_ready

    @pyqtSlot(str)
    def setStageMode(self, mode: str) -> None:
        self._stage_mode = mode or "presence"
        self.stageModeChanged.emit()

    @pyqtSlot(float)
    def setSpeechLevel(self, level: float) -> None:
        self._speech_level = max(0.0, min(1.0, float(level)))
        self.speechLevelChanged.emit()
