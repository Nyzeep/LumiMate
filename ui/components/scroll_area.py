from __future__ import annotations

from PyQt6.QtWidgets import QScrollArea


class ModernScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(self.Shape.NoFrame)
        self.setStyleSheet("QScrollArea { background: transparent; border: 0; }")
