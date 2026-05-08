from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGridLayout, QLabel

from ui.components import PageContainer, SceneCard


class SettingsPage(PageContainer):
    def __init__(self, parent=None):
        super().__init__(parent, margins=(48, 40, 48, 40), spacing=20)
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("设置")
        title.setFont(QFont("Microsoft YaHei UI", 30, QFont.Weight.DemiBold))
        subtitle = QLabel("只保留会影响陪伴体验的选择。")
        subtitle.setStyleSheet("color: rgba(238,243,245,0.62);")
        self.root.addWidget(title)
        self.root.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)
        items = [
            ("外观", "静夜梦境", "雾面背景、柔和对比与低饱和色彩。"),
            ("性能", "平衡", "慢速动画与轻量重绘。"),
            ("音频", "默认设备", "录音、播放与语音互动。"),
            ("Live2D", "预留", "未来角色运行时入口。"),
            ("启动", "进入首页", "打开后回到 Lumi 的空间。"),
            ("实验功能", "关闭", "暂不启用未完成能力。"),
        ]
        for index, (name, value, detail) in enumerate(items):
            grid.addWidget(SceneCard(name, value, detail), index // 2, index % 2)
        self.root.addLayout(grid)
        self.root.addStretch()
