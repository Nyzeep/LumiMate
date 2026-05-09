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
                background-color: rgba(3, 8, 18, 0.34);
                border: 0px;
                border-bottom: 1px solid rgba(201,217,226,0.20);
                border-radius: 0px;
                padding: 8px 10px;
                color: {Theme.text};
                selection-background-color: rgba(217,120,85,0.42);
            }}
            QLineEdit:hover {{
                background-color: rgba(9,17,30,0.42);
                border-bottom-color: rgba(201,217,226,0.34);
            }}
            QLineEdit:focus {{
                background-color: rgba(13,24,42,0.54);
                border-bottom-color: rgba(217,120,85,0.72);
            }}
            """
        )
