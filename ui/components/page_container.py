from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QWidget


class PageContainer(QWidget):
    def __init__(self, parent=None, margins: tuple[int, int, int, int] = (24, 22, 24, 22), spacing: int = 18):
        super().__init__(parent)
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(*margins)
        self.root.setSpacing(spacing)
