from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from ui.components import BreathingLabel, CompanionScene, PageContainer, PoeticPanel, QuietActionButton, SceneCard


class HomePage(PageContainer):
    open_chat_requested = pyqtSignal()
    open_companion_requested = pyqtSignal()
    open_workbench_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, margins=(48, 38, 42, 36), spacing=20)
        self._build_ui()

    def _build_ui(self) -> None:
        hour = datetime.now().hour
        greeting = "晚上好，星辰" if hour >= 18 else "欢迎回来，星辰"
        subtitle = "Lumi 正在安静地等你。"

        hero = QHBoxLayout()
        hero.setSpacing(24)

        left = QVBoxLayout()
        left.setSpacing(22)
        time_label = QLabel(datetime.now().strftime("%H:%M\n%m月%d日"))
        time_label.setStyleSheet("color: rgba(238,243,245,0.62); font-size: 14px;")
        title = QLabel(greeting)
        title.setFont(QFont("Microsoft YaHei UI", 33, QFont.Weight.DemiBold))
        title.setStyleSheet("color: rgba(255,255,255,0.94);")
        breath = BreathingLabel(subtitle)
        breath.setFont(QFont("Microsoft YaHei UI", 15))
        left.addWidget(time_label)
        left.addSpacing(12)
        left.addWidget(title)
        left.addWidget(breath)
        left.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(12)
        chat = QuietActionButton("开始对话", "和 Lumi 说说话")
        companion = QuietActionButton("进入陪伴", "靠近她的世界")
        workbench = QuietActionButton("打开工作台", "整理模型与语音")
        chat.clicked.connect(self.open_chat_requested.emit)
        companion.clicked.connect(self.open_companion_requested.emit)
        workbench.clicked.connect(self.open_workbench_requested.emit)
        actions.addWidget(chat)
        actions.addWidget(companion)
        actions.addWidget(workbench)
        left.addLayout(actions)

        scene_panel = PoeticPanel(radius=28)
        scene_layout = QVBoxLayout(scene_panel)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene = CompanionScene("home")
        scene.setMinimumHeight(520)
        scene_layout.addWidget(scene)
        hero.addLayout(left, 4)
        hero.addWidget(scene_panel, 8)
        self.root.addLayout(hero, 1)

        bottom = QHBoxLayout()
        bottom.setSpacing(18)
        bottom.addWidget(SceneCard("Lumi 状态", "在线", "她在静静地等待。", warm=True))
        bottom.addWidget(SceneCard("情绪", "平静", "呼吸与光线保持柔和。", warm=True))
        bottom.addWidget(SceneCard("今日小记", "还没有新的记忆", "开始一次对话，让今天留下痕迹。", warm=True))
        self.root.addLayout(bottom)
