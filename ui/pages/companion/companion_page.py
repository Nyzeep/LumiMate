from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from ui.components import CompanionScene, PageContainer, PoeticPanel, QuietActionButton, SceneCard


class CompanionPage(PageContainer):
    def __init__(self, parent=None):
        super().__init__(parent, margins=(42, 32, 34, 32), spacing=18)
        self._emotion = "平静"
        self._presence = "待机"
        self._build_ui()

    def _build_ui(self) -> None:
        body = QHBoxLayout()
        body.setSpacing(28)
        scene_panel = PoeticPanel(radius=30)
        scene_layout = QVBoxLayout(scene_panel)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene = CompanionScene("companion")
        scene.setMinimumHeight(620)
        scene_layout.addWidget(scene)
        body.addWidget(scene_panel, 8)

        side = QVBoxLayout()
        side.setSpacing(14)
        title = QLabel("陪伴空间")
        title.setFont(QFont("Microsoft YaHei UI", 28, QFont.Weight.DemiBold))
        subtitle = QLabel("这里是 Lumi 的世界。未来的 Live2D、Spine、呼吸、视线与细微反应都会在这里生长。")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: rgba(238,243,245,0.66); line-height: 1.4;")
        side.addWidget(title)
        side.addWidget(subtitle)
        self.emotion_card = SceneCard("情绪", self._emotion, "环境光会跟随情绪变化。", warm=True)
        self.presence_card = SceneCard("陪伴状态", self._presence, "她正在安静地等待。", warm=True)
        side.addWidget(self.emotion_card)
        side.addWidget(self.presence_card)
        side.addSpacing(8)
        side.addWidget(QuietActionButton("换装", "预留角色服装与外观"))
        side.addWidget(QuietActionButton("背景", "预留场景与时间切换"))
        side.addWidget(QuietActionButton("动作", "预留 Live2D / Spine 触发"))
        side.addWidget(QuietActionButton("记忆碎片", "查看与整理长期记忆"))
        side.addStretch()

        body.addLayout(side, 4)
        self.root.addLayout(body, 1)

    def set_emotion(self, emotion: str) -> None:
        self._emotion = emotion

    def set_presence_state(self, state: str) -> None:
        self._presence = state
