from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QPushButton

from ui.themes import Theme


class AnimatedButton(QPushButton):
    def __init__(self, text: str = "", parent=None, primary: bool = False):
        super().__init__(text, parent)
        self.primary = primary
        self._glow = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(16)
        self._shadow.setOffset(0, 7)
        self._shadow.setColor(QColor(0, 0, 0, 92))
        self.setGraphicsEffect(self._shadow)
        self._style()

    @pyqtProperty(float)
    def glow(self) -> float:
        return self._glow

    @glow.setter
    def glow(self, value: float) -> None:
        self._glow = value
        self._shadow.setBlurRadius(16 + int(value * 12))
        self._style()

    def _style(self) -> None:
        bg = (
            f"rgba(226,118,79,{0.84 + self._glow * 0.08:.3f})"
            if self.primary
            else f"rgba(18,29,46,{0.72 + self._glow * 0.08:.3f})"
        )
        border = "rgba(244,164,118,0.58)" if self.primary else f"rgba(180,204,228,{0.18 + self._glow * 0.16:.3f})"
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 14px;
                padding: 8px 15px;
                color: {Theme.text};
                font-weight: 700;
            }}
            QPushButton:hover {{
                border-color: rgba(244,164,118,0.72);
            }}
            QPushButton:pressed {{
                padding-top: 9px;
                padding-bottom: 7px;
            }}
            QPushButton:disabled {{
                color: rgba(244,248,251,0.38);
                background-color: rgba(18,29,46,0.38);
                border-color: rgba(180,204,228,0.08);
            }}
            """
        )

    def enterEvent(self, event) -> None:
        self._animate(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate(0.0)
        super().leaveEvent(event)

    def _animate(self, value: float) -> None:
        animation = QPropertyAnimation(self, b"glow", self)
        animation.setDuration(Theme.motion.hover)
        animation.setEndValue(value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class GlassButton(AnimatedButton):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text=text, parent=parent, primary=False)


class GlowButton(AnimatedButton):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text=text, parent=parent, primary=True)


class NavigationItem(QPushButton):
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.label = text
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(QSize(100, 48))
        self.setText(f"{icon}  {text}")
        self.setToolTip(text)
        self._style()

    def set_expanded(self, expanded: bool) -> None:
        return

    def _style(self) -> None:
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 13px;
                padding: 8px 11px;
                color: rgba(244,248,251,0.70);
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }}
            QPushButton:hover {{
                color: {Theme.text};
                background-color: rgba(18,29,46,0.74);
                border-color: rgba(180,204,228,0.18);
            }}
            QPushButton:checked {{
                color: {Theme.text};
                background-color: rgba(226,118,79,0.20);
                border-color: rgba(226,118,79,0.52);
            }}
            """
        )


SidebarButton = NavigationItem
