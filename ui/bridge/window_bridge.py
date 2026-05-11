from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot


class WindowBridge(QObject):
    windowModeChanged = Signal()

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self._window = window

    @Property(bool, notify=windowModeChanged)
    def isFullscreen(self) -> bool:
        return bool(self._window and self._window.isFullScreen())

    @Slot(result=bool)
    def minimize(self) -> bool:
        if not self._window:
            return False
        self._window.showMinimized()
        return True

    @Slot(result=bool)
    def close(self) -> bool:
        if not self._window:
            return False
        self._window.close()
        return True

    @Slot(result=bool)
    def toggleWindowMode(self) -> bool:
        if not self._window:
            return False
        if self._window.isFullScreen():
            self._window.showNormal()
            self._window.resize(1600, 900)
        else:
            self._window.showFullScreen()
        self.windowModeChanged.emit()
        return True

    @Slot(int, int, result=bool)
    def moveBy(self, dx: int, dy: int) -> bool:
        if not self._window or self._window.isFullScreen():
            return False
        position = self._window.pos()
        self._window.move(position.x() + int(dx), position.y() + int(dy))
        return True
