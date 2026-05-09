from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from ui.components import CompanionScene, FloatingInputBar, OrbitalNodeButton, PageContainer, PresenceTranscript, SceneCard


class ChatPage(PageContainer):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    send_requested = pyqtSignal(str)
    open_workbench_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, margins=(40, 30, 34, 30), spacing=18)
        self._ready = False
        self._running = False
        self._build_ui()

    def _build_ui(self) -> None:
        body = QHBoxLayout()
        body.setSpacing(24)

        conversation = QVBoxLayout()
        conversation.setSpacing(14)
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("对话空间")
        title.setFont(QFont("Microsoft YaHei UI", 28, QFont.Weight.DemiBold))
        title.setStyleSheet("color: rgba(243,225,206,0.96);")
        subtitle = QLabel("声音与文字会慢慢浮现，不必急着回答。")
        subtitle.setStyleSheet("color: rgba(242,237,229,0.56);")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        self.status_label = QLabel("请先在工作台唤醒 Lumi")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet("color: rgba(184,206,217,0.70); font-weight: 650;")
        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(self.status_label)
        conversation.addLayout(header)

        self.transcript = PresenceTranscript()
        conversation.addWidget(self.transcript, 1)

        self.input_bar = FloatingInputBar()
        self.input_bar.start_requested.connect(self.start_requested.emit)
        self.input_bar.stop_requested.connect(self.stop_requested.emit)
        self.input_bar.send_requested.connect(self._send_text)
        self.input_bar.clear_requested.connect(self.clear_chat)
        self.input_bar.clear_requested.connect(self.clear_requested.emit)
        self.input_bar.voice_button.setEnabled(False)
        conversation.addWidget(self.input_bar)

        side = QVBoxLayout()
        side.setSpacing(14)
        scene = CompanionScene("chat")
        scene.setMinimumWidth(280)
        scene.setMinimumHeight(500)
        side.addWidget(scene, 1)
        side.addWidget(SceneCard("聆听状态", "待机", "Lumi 会在你点亮声音后靠近。", warm=True))
        self.wake_button = OrbitalNodeButton("前往唤醒 Lumi", "workbench", "加载模型后开始对话", node_size=58)
        self.wake_button.clicked.connect(self.open_workbench_requested.emit)
        side.addWidget(self.wake_button)

        body.addLayout(conversation, 7)
        body.addLayout(side, 4)
        self.root.addLayout(body, 1)

    def set_running(self, running: bool) -> None:
        self._running = running
        self.status_label.setText("正在聆听" if running else ("已经准备好" if self._ready else "请先在工作台唤醒 Lumi"))
        self.input_bar.set_running(running)
        self.input_bar.set_ready(self._ready)
        self.input_bar.voice_button.setEnabled(self._ready and not running)

    def set_ready(self, ready: bool) -> None:
        self._ready = ready
        self.input_bar.set_ready(ready)
        self.input_bar.voice_button.setEnabled(ready and not self._running)
        self.wake_button.setVisible(not ready)
        if self._running:
            self.status_label.setText("正在聆听")
        else:
            self.status_label.setText("已经准备好" if ready else "请先在工作台唤醒 Lumi")

    def set_status(self, message: str) -> None:
        self.status_label.setText(message)

    def is_ready(self) -> bool:
        return self._ready

    def is_running(self) -> bool:
        return self._running

    def add_message(self, text: str, is_user: bool) -> None:
        self.transcript.add_message(text, is_user)
        QTimer.singleShot(80, lambda: self.transcript.verticalScrollBar().setValue(
            self.transcript.verticalScrollBar().maximum()
        ))

    def clear_chat(self) -> None:
        self.transcript.clear()

    def _send_text(self, text: str) -> None:
        self.send_requested.emit(text)
