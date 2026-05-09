from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from ui.components import CompanionScene, OrbitalNodeButton, PageContainer, SceneCard


class CompanionPage(PageContainer):
    def __init__(self, parent=None):
        super().__init__(parent, margins=(40, 30, 34, 30), spacing=18)
        self._emotion = "平静"
        self._presence = "待机"
        self._build_ui()

    def _build_ui(self) -> None:
        body = QHBoxLayout()
        body.setSpacing(28)
        scene = CompanionScene("companion")
        scene.setMinimumHeight(620)
        body.addWidget(scene, 7)

        side = QVBoxLayout()
        side.setSpacing(14)
        title = QLabel("陪伴空间")
        title.setFont(QFont("Microsoft YaHei UI", 28, QFont.Weight.DemiBold))
        title.setStyleSheet("color: rgba(243,225,206,0.96);")
        subtitle = QLabel("这里不是资料页，而是 Lumi 的夜间世界。情绪、记忆与呼吸会在光里慢慢改变。")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: rgba(242,237,229,0.62); line-height: 1.4;")
        side.addWidget(title)
        side.addWidget(subtitle)
        self.emotion_card = SceneCard("情绪", self._emotion, "环境光会跟随情绪变化。", warm=True)
        self.presence_card = SceneCard("陪伴状态", self._presence, "她正在安静地等待。", warm=True)
        memory_card = SceneCard("记忆碎片", "三段微光", "对话、停顿、夜色都会成为片段。")
        side.addWidget(self.emotion_card)
        side.addWidget(self.presence_card)
        side.addWidget(memory_card)
        side.addSpacing(8)
        side.addWidget(OrbitalNodeButton("更换氛围", "orbit", "预留服装与场景切换", node_size=58))
        side.addWidget(OrbitalNodeButton("轻触动作", "spark", "预留 Live2D / Spine 触发", node_size=58))
        side.addWidget(OrbitalNodeButton("整理记忆", "ring", "查看与整理长期记忆", node_size=58))
        side.addStretch()

        body.addLayout(side, 4)
        self.root.addLayout(body, 1)

    def set_emotion(self, emotion: str) -> None:
        self._emotion = emotion
        self.emotion_card.set_value(emotion)

    def set_presence_state(self, state: str) -> None:
        self._presence = state
        self.presence_card.set_value(state)
