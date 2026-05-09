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
        self.setFixedWidth(158)
        self.setObjectName("minimalNavRail")
        self.setStyleSheet(
            f"""
            QWidget#minimalNavRail {{
                background-color: rgba(3, 8, 20, 0.78);
                border-right: 1px solid rgba(180,204,228,0.12);
                border-radius: 0px;
            }}
            """
        )
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 24, 16, 18)
        layout.setSpacing(12)

        brand = QLabel("△  LumiMate")
        brand.setStyleSheet(f"color: {Theme.text}; font-size: 15px; font-weight: 800;")
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
            "color: rgba(244,248,251,0.62); font-size: 11px; line-height: 1.4;"
            "background-color: rgba(18,29,46,0.72); border: 1px solid rgba(180,204,228,0.12);"
            "border-radius: 16px; padding: 12px;"
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
