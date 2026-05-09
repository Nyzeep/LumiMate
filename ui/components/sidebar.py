from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.components.buttons import NavigationItem
from ui.themes import Theme


class FloatingSidebar(QWidget):
    page_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: dict[str, NavigationItem] = {}
        self.setFixedWidth(154)
        self.setObjectName("minimalNavRail")
        self.setStyleSheet(
            """
            QWidget#minimalNavRail {
                background-color: rgba(2, 7, 19, 0.46);
                border-right: 1px solid rgba(201,217,226,0.10);
            }
            """
        )
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 20, 16, 18)
        layout.setSpacing(10)

        brand = QLabel("△  LumiMate")
        brand.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        brand.setStyleSheet(f"color: {Theme.text};")
        subtitle = QLabel("数字陪伴空间")
        subtitle.setStyleSheet("color: rgba(242,237,229,0.52); font-size: 11px; padding-left: 22px;")
        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addSpacing(22)

        primary_items = [
            ("home", "△", "首页"),
            ("chat", "○", "对话"),
            ("companion", "✦", "陪伴"),
        ]
        secondary_items = [
            ("workbench", "∩", "工作台"),
            ("settings", "·", "设置"),
        ]
        for key, icon, label in primary_items:
            self._add_item(layout, key, icon, label)
        layout.addStretch()
        for key, icon, label in secondary_items:
            self._add_item(layout, key, icon, label)

        footer = QLabel("星辰\n与 LumiMate 一起")
        footer.setStyleSheet(
            "color: rgba(242,237,229,0.56); font-size: 11px; line-height: 1.4;"
            "border-top: 1px solid rgba(201,217,226,0.12); padding-top: 12px;"
        )
        layout.addSpacing(10)
        layout.addWidget(footer)

    def _add_item(self, layout: QVBoxLayout, key: str, icon: str, label: str) -> None:
        item = NavigationItem(icon, label)
        item.clicked.connect(lambda checked=False, page_key=key: self.page_requested.emit(page_key))
        self.items[key] = item
        layout.addWidget(item)

    def select(self, key: str) -> None:
        for item_key, item in self.items.items():
            item.setChecked(item_key == key)
