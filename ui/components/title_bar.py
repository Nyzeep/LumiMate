from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from ui.themes import Theme


class TitleBar(QWidget):
    minimize_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_position: QPoint | None = None
        self.setFixedHeight(42)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 7, 12, 7)
        layout.setSpacing(10)
        title = QLabel("LumiMate")
        title.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        subtitle = QLabel("静夜陪伴空间")
        subtitle.setStyleSheet(f"color: rgba(244,248,251,0.56); font-size: 12px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.min_button = self._window_button("－")
        self.max_button = self._window_button("□")
        self.close_button = self._window_button("×", danger=True)
        self.min_button.clicked.connect(self.minimize_requested.emit)
        self.max_button.clicked.connect(self.maximize_requested.emit)
        self.close_button.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)

    def _window_button(self, text: str, danger: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(32, 26)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        hover = "rgba(226,118,79,0.28)" if danger else "rgba(180,204,228,0.12)"
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(18,29,46,0.58);
                border: 1px solid rgba(180,204,228,0.12);
                border-radius: 10px;
                color: {Theme.text};
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            """
        )
        return button

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.window():
            self._drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_position is not None and event.buttons() & Qt.MouseButton.LeftButton and self.window():
            self.window().move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_position = None
        super().mouseReleaseEvent(event)
