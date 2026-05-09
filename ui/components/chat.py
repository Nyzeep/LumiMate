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
        bg = "rgba(226,118,79,0.20)" if is_user else "rgba(18,29,46,0.82)"
        border = "rgba(226,118,79,0.44)" if is_user else "rgba(180,204,228,0.16)"
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 18px;
                {align_radius}: 6px;
                color: {Theme.text};
                padding: 12px 16px;
            }}
            """
        )
