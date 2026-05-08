from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.components.buttons import NavigationItem
from ui.themes import Theme


class FloatingSidebar(QWidget):
    page_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: dict[str, NavigationItem] = {}
        self.setFixedWidth(136)
        self.setObjectName("minimalNavRail")
        self.setStyleSheet(
            f"""
            QWidget#minimalNavRail {{
                background-color: rgba(8, 24, 38, 0.68);
                border-right: 1px solid rgba(255,255,255,0.08);
                border-radius: 0px;
            }}
            """
        )
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 24, 14, 18)
        layout.setSpacing(12)

        brand = QLabel("△  LumiMate")
        brand.setStyleSheet(f"color: {Theme.text}; font-size: 14px; font-weight: 800;")
        layout.addWidget(brand)
        layout.addSpacing(24)

        items = [
            ("home", "⌂", "首页"),
            ("chat", "●", "对话"),
            ("companion", "✦", "陪伴"),
            ("workbench", "▧", "工作台"),
            ("settings", "⚙", "设置"),
        ]
        for key, icon, label in items[:3]:
            self._add_item(layout, key, icon, label)
        layout.addStretch()
        for key, icon, label in items[3:]:
            self._add_item(layout, key, icon, label)

        footer = QLabel("星辰\n与 LumiMate 一起")
        footer.setStyleSheet(
            "color: rgba(238,243,245,0.58); font-size: 11px; line-height: 1.4;"
            "background-color: rgba(239,246,248,0.09); border-radius: 18px; padding: 12px;"
        )
        layout.addSpacing(12)
        layout.addWidget(footer)

    def _add_item(self, layout: QVBoxLayout, key: str, icon: str, label: str) -> None:
        item = NavigationItem(icon, label)
        item.clicked.connect(lambda checked=False, page_key=key: self.page_requested.emit(page_key))
        self.items[key] = item
        layout.addWidget(item)

    def select(self, key: str) -> None:
        for item_key, item in self.items.items():
            item.setChecked(item_key == key)
