from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.components.scroll_area import ModernScrollArea
from ui.themes import Theme


class ChatBubble(QLabel):
    """Compatibility wrapper for older call sites."""

    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setMaximumWidth(620)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setFont(QFont("Microsoft YaHei UI", 12 if is_user else 13))
        color = "rgba(242,237,229,0.88)" if is_user else "rgba(243,225,206,0.94)"
        self.setStyleSheet(
            f"""
            QLabel {{
                background: transparent;
                border: 0;
                color: {color};
                padding: 8px 4px;
                line-height: 1.5;
            }}
            """
        )


class PresenceTranscript(ModernScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.lines = QVBoxLayout(self.container)
        self.lines.setContentsMargins(4, 18, 4, 18)
        self.lines.setSpacing(22)
        self.lines.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.container)

    def add_message(self, text: str, is_user: bool) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        line = QWidget()
        line_layout = QVBoxLayout(line)
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setSpacing(4)
        speaker = QLabel("你" if is_user else "Lumi")
        speaker.setStyleSheet(
            f"color: {'rgba(217,120,85,0.76)' if is_user else 'rgba(184,206,217,0.70)'}; "
            "font-size: 11px; font-weight: 700;"
        )
        body = ChatBubble(text, is_user)
        line_layout.addWidget(speaker)
        line_layout.addWidget(body)
        line.setMaximumWidth(680)

        if is_user:
            row.addStretch(2)
            row.addWidget(line, 5)
        else:
            row.addWidget(line, 6)
            row.addStretch(2)
        self.lines.addLayout(row)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear(self) -> None:
        while self.lines.count():
            item = self.lines.takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                item.layout().deleteLater()
            elif item.widget():
                item.widget().deleteLater()
