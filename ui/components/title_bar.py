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
        self.setFixedHeight(46)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 14, 7)
        layout.setSpacing(10)
        title = QLabel("LumiMate")
        title.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        subtitle = QLabel("静夜陪伴空间")
        subtitle.setStyleSheet(f"color: rgba(242,237,229,0.52); font-size: 12px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        ambient = self._window_button("♪")
        ambient.setToolTip("夜间氛围")
        self.min_button = self._window_button("−")
        self.max_button = self._window_button("□")
        self.close_button = self._window_button("×", danger=True)
        self.min_button.clicked.connect(self.minimize_requested.emit)
        self.max_button.clicked.connect(self.maximize_requested.emit)
        self.close_button.clicked.connect(self.close_requested.emit)
        layout.addWidget(ambient)
        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)

    def _window_button(self, text: str, danger: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(34, 34)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        hover = "rgba(217,120,85,0.26)" if danger else "rgba(201,217,226,0.13)"
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(7,14,27,0.30);
                border: 1px solid rgba(201,217,226,0.12);
                border-radius: 17px;
                color: {Theme.text};
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {hover};
                border-color: rgba(243,225,206,0.28);
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
