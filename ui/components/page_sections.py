from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.components.buttons import GlassButton
from ui.components.geometric import OrbitalNodeButton
from ui.components.poetic import CompanionScene, SceneCard
from ui.themes import Theme


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str = "", eyebrow: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        if eyebrow:
            eyebrow_label = QLabel(eyebrow)
            eyebrow_label.setStyleSheet("color: rgba(242,237,229,0.58); font-size: 12px; font-weight: 700;")
            layout.addWidget(eyebrow_label)
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei UI", 28, QFont.Weight.DemiBold))
        title_label.setStyleSheet(f"color: {Theme.text};")
        layout.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setWordWrap(True)
            subtitle_label.setStyleSheet("color: rgba(242,237,229,0.68); font-size: 13px;")
            layout.addWidget(subtitle_label)


class InfoCard(SceneCard):
    pass


class QuickActionCard(OrbitalNodeButton):
    def __init__(self, title: str, detail: str, button_text: str = "进入", parent=None):
        super().__init__(title, "orbit", detail, parent=parent)
        self.button = self


class CompanionStage(QWidget):
    def __init__(self, title: str = "Lumi", subtitle: str = "正在安静地陪伴你", compact: bool = False, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(260 if compact else 360)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        scene = CompanionScene("chat" if compact else "home")
        scene.setMinimumHeight(260 if compact else 360)
        layout.addWidget(scene, 1)
        caption = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.DemiBold))
        detail_label = QLabel(subtitle)
        detail_label.setWordWrap(True)
        detail_label.setStyleSheet("color: rgba(242,237,229,0.64);")
        caption.addWidget(title_label)
        caption.addStretch()
        caption.addWidget(detail_label)
        layout.addLayout(caption)
