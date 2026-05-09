from __future__ import annotations

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class AmbientClock(QObject):
    """Shared low-frequency clock for the breathing Lumi UI world."""

    tick = pyqtSignal(float)

    _instance: "AmbientClock | None" = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(33)

    @classmethod
    def instance(cls) -> "AmbientClock":
        if cls._instance is None:
            cls._instance = AmbientClock()
        return cls._instance

    @property
    def phase(self) -> float:
        return self._phase

    def _advance(self) -> None:
        self._phase = (self._phase + 0.010) % 6283.0
        self.tick.emit(self._phase)
