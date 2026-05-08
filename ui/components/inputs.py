from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit

from ui.themes import Theme


class FloatingInput(QLineEdit):
    def __init__(self, hint: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(hint)
        self.setMinimumHeight(40)
        self.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: rgba(239,246,248,0.12);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 18px;
                padding: 8px 13px;
                color: {Theme.text};
            }}
            QLineEdit:hover {{
                background-color: rgba(239,246,248,0.16);
                border-color: rgba(255,255,255,0.22);
            }}
            QLineEdit:focus {{
                background-color: rgba(239,246,248,0.18);
                border-color: rgba(185,220,228,0.46);
            }}
            """
        )
