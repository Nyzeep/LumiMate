from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel

from ui.themes import Theme


class ChatBubble(QLabel):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setMaximumWidth(520)
        self.setFont(QFont("Microsoft YaHei UI", 10))
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        align_radius = "border-top-right-radius" if is_user else "border-top-left-radius"
        bg = "rgba(239,246,248,0.18)" if is_user else "rgba(9,27,43,0.48)"
        border = "rgba(255,255,255,0.18)" if is_user else "rgba(255,255,255,0.11)"
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 22px;
                {align_radius}: 6px;
                color: {Theme.text};
                padding: 12px 16px;
            }}
            """
        )
