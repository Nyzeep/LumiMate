from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot


class ShellBridge(QObject):
    bootPhaseChanged = Signal()
    frontendReadyRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._boot_phase = "starting"
        self._frontend_ready = False

    @Property(str, notify=bootPhaseChanged)
    def bootPhase(self) -> str:
        return self._boot_phase

    @Slot(result=bool)
    def frontendReady(self) -> bool:
        if self._frontend_ready:
            return False
        self._frontend_ready = True
        self._set_phase("frontend-ready")
        self.frontendReadyRequested.emit()
        return True

    def set_phase(self, phase: str) -> None:
        self._set_phase(phase)

    def _set_phase(self, phase: str) -> None:
        phase = (phase or "").strip() or "starting"
        if phase == self._boot_phase:
            return
        self._boot_phase = phase
        self.bootPhaseChanged.emit()
