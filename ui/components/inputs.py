from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit, QSizePolicy

from ui.themes import Theme


class FloatingInput(QLineEdit):
    def __init__(self, hint: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(hint)
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: rgba(9, 17, 30, 0.58);
                border: 1px solid rgba(180,204,228,0.18);
                border-radius: 14px;
                padding: 8px 13px;
                color: {Theme.text};
            }}
            QLineEdit:hover {{
                background-color: rgba(18,29,46,0.72);
                border-color: rgba(180,204,228,0.30);
            }}
            QLineEdit:focus {{
                background-color: rgba(18,29,46,0.82);
                border-color: rgba(226,118,79,0.62);
            }}
            """
        )
