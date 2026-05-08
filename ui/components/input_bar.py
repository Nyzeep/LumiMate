from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout

from ui.components.buttons import GlassButton, GlowButton
from ui.components.inputs import FloatingInput
from ui.components.poetic import PoeticPanel


class FloatingInputBar(PoeticPanel):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    send_requested = pyqtSignal(str)
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent, radius=26)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        self.input = FloatingInput("把想说的话留在这里")
        self.input.setEnabled(False)
        self.voice_button = GlowButton("开始聆听")
        self.stop_button = GlassButton("停下")
        self.send_button = GlassButton("发送")
        self.clear_button = GlassButton("清空")
        self.stop_button.setEnabled(False)
        self.voice_button.clicked.connect(self.start_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        self.send_button.clicked.connect(lambda: self.send_requested.emit(self.input.text()))
        self.clear_button.clicked.connect(self.clear_requested.emit)
        layout.addWidget(self.input, 1)
        layout.addWidget(self.voice_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.send_button)
        layout.addWidget(self.clear_button)

    def set_running(self, running: bool) -> None:
        self.voice_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
