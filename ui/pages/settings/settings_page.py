from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGridLayout, QLabel

from ui.components import PageContainer, SceneCard


class SettingsPage(PageContainer):
    def __init__(self, parent=None):
        super().__init__(parent, margins=(42, 30, 42, 30), spacing=20)
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("设置")
        title.setFont(QFont("Microsoft YaHei UI", 30, QFont.Weight.DemiBold))
        title.setStyleSheet("color: rgba(243,225,206,0.96);")
        subtitle = QLabel("只保留会影响陪伴体验的部分。其它内容都退到更深的层级里。")
        subtitle.setStyleSheet("color: rgba(242,237,229,0.62);")
        self.root.addWidget(title)
        self.root.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        items = [
            ("外观", "静夜梦境", "低饱和夜色、柔光与负空间。"),
            ("性能", "平衡", "在氛围与长期运行之间取中点。"),
            ("音频", "默认设备", "录音、播放与语音交互。"),
            ("Live2D", "预留", "未来角色运动入口。"),
            ("启动", "回到首页", "打开后先进入 Lumi 的空间。"),
            ("实验功能", "关闭", "暂不显示未完成能力。"),
        ]
        for index, (name, value, detail) in enumerate(items):
            grid.addWidget(SceneCard(name, value, detail), index // 2, index % 2)
        self.root.addLayout(grid)
        self.root.addStretch()
