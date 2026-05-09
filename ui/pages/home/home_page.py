from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from ui.components import BreathingLabel, CompanionScene, OrbitalNodeButton, PageContainer, SceneCard


class HomePage(PageContainer):
    open_chat_requested = pyqtSignal()
    open_companion_requested = pyqtSignal()
    open_workbench_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, margins=(42, 30, 34, 30), spacing=18)
        self._build_ui()

    def _build_ui(self) -> None:
        now = datetime.now()
        greeting = "晚上好，星辰" if now.hour >= 18 or now.hour < 6 else "欢迎回来，星辰"

        hero = QHBoxLayout()
        hero.setSpacing(24)

        left = QVBoxLayout()
        left.setSpacing(12)
        time_label = QLabel(now.strftime("%H:%M  ·  %m月%d日"))
        time_label.setStyleSheet("color: rgba(242,237,229,0.58); font-size: 13px;")
        title = QLabel(greeting)
        title.setFont(QFont("Microsoft YaHei UI", 32, QFont.Weight.DemiBold))
        title.setStyleSheet("color: rgba(243,225,206,0.96);")
        breath = BreathingLabel("Lumi 正在安静地等你")
        breath.setFont(QFont("Microsoft YaHei UI", 15))
        left.addWidget(time_label)
        left.addSpacing(26)
        left.addWidget(title)
        left.addWidget(breath)
        left.addSpacing(24)

        status = SceneCard("Lumi 状态", "在线", "光线柔和，呼吸稳定。", warm=True)
        memory = SceneCard("今日小记", "还没有新的记忆", "开始一次对话，让今天留下温度。", warm=False)
        left.addWidget(status)
        left.addWidget(memory)
        left.addStretch()

        scene = CompanionScene("home")
        scene.setMinimumHeight(500)
        hero.addLayout(left, 4)
        hero.addWidget(scene, 7)
        self.root.addLayout(hero, 1)

        actions = QHBoxLayout()
        actions.setSpacing(16)
        chat = OrbitalNodeButton("开始对话", "chat", "与 Lumi 聊聊今日心情")
        companion = OrbitalNodeButton("进入陪伴空间", "companion", "靠近 Lumi 的世界")
        workbench = OrbitalNodeButton("唤醒核心", "workbench", "模型与声音初始化")
        chat.clicked.connect(self.open_chat_requested.emit)
        companion.clicked.connect(self.open_companion_requested.emit)
        workbench.clicked.connect(self.open_workbench_requested.emit)
        actions.addWidget(chat)
        actions.addWidget(companion)
        actions.addWidget(workbench)
        self.root.addLayout(actions)
