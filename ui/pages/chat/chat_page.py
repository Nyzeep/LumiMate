from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.components import ChatBubble, CompanionScene, FloatingInputBar, ModernScrollArea, PageContainer, PoeticPanel


class ChatPage(PageContainer):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, margins=(42, 32, 34, 32), spacing=18)
        self._ready = False
        self._running = False
        self._build_ui()

    def _build_ui(self) -> None:
        body = QHBoxLayout()
        body.setSpacing(22)

        chat_panel = PoeticPanel(radius=34)
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(24, 24, 24, 18)
        chat_layout.setSpacing(16)
        header = QHBoxLayout()
        title = QLabel("聊天")
        title.setFont(QFont("Microsoft YaHei UI", 28, QFont.Weight.DemiBold))
        self.status_label = QLabel("请先在工作台加载模型")
        self.status_label.setStyleSheet("color: rgba(238,243,245,0.60); font-weight: 650;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_label)
        chat_layout.addLayout(header)

        self.chat_scroll = ModernScrollArea()
        self.chat_container = QWidget()
        self.chat_bubbles = QVBoxLayout(self.chat_container)
        self.chat_bubbles.setContentsMargins(2, 14, 2, 14)
        self.chat_bubbles.setSpacing(16)
        self.chat_bubbles.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_container)
        chat_layout.addWidget(self.chat_scroll, 1)

        self.input_bar = FloatingInputBar()
        self.input_bar.start_requested.connect(self.start_requested.emit)
        self.input_bar.stop_requested.connect(self.stop_requested.emit)
        self.input_bar.clear_requested.connect(self.clear_chat)
        self.input_bar.clear_requested.connect(self.clear_requested.emit)
        self.input_bar.voice_button.setEnabled(False)
        chat_layout.addWidget(self.input_bar)

        scene_panel = PoeticPanel(radius=30)
        scene_wrap = QVBoxLayout(scene_panel)
        scene_wrap.setContentsMargins(22, 22, 22, 22)
        scene_wrap.setSpacing(12)
        scene_title = QLabel("Lumi")
        scene_title.setFont(QFont("Microsoft YaHei UI", 24, QFont.Weight.DemiBold))
        scene_hint = QLabel("她会一直在这里。")
        scene_hint.setStyleSheet("color: rgba(238,243,245,0.62);")
        scene = CompanionScene("chat")
        scene.setMinimumWidth(360)
        scene.setMinimumHeight(500)
        scene_wrap.addWidget(scene_title)
        scene_wrap.addWidget(scene_hint)
        scene_wrap.addWidget(scene, 1)

        body.addWidget(chat_panel, 7)
        body.addWidget(scene_panel, 5)
        self.root.addLayout(body, 1)

    def set_running(self, running: bool) -> None:
        self._running = running
        self.status_label.setText("正在聆听" if running else ("已准备" if self._ready else "请先在工作台加载模型"))
        self.input_bar.set_running(running)
        self.input_bar.voice_button.setEnabled(self._ready and not running)

    def set_ready(self, ready: bool) -> None:
        self._ready = ready
        self.input_bar.voice_button.setEnabled(ready and not self._running)
        if self._running:
            self.status_label.setText("正在聆听")
        else:
            self.status_label.setText("已准备" if ready else "请先在工作台加载模型")

    def add_message(self, text: str, is_user: bool) -> None:
        bubble = ChatBubble(text, is_user)
        row = QHBoxLayout()
        if is_user:
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()
        self.chat_bubbles.addLayout(row)
        QTimer.singleShot(80, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))

    def clear_chat(self) -> None:
        while self.chat_bubbles.count():
            item = self.chat_bubbles.takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                item.layout().deleteLater()
            elif item.widget():
                item.widget().deleteLater()
