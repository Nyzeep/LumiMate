from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect

from ui.themes import Theme


class GlassCard(QFrame):
    def __init__(self, parent=None, radius: int | None = None, padding: int = 0, elevated: bool = True):
        super().__init__(parent)
        self.radius = radius or Theme.radii.lg
        self.padding = padding
        self._base_blur = 24 if elevated else 12
        self._hover_blur = 34 if elevated else 20
        self.setObjectName("glassCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(self._base_blur)
        self._shadow.setOffset(0, 10 if elevated else 4)
        self._shadow.setColor(Theme.shadow)
        self.setGraphicsEffect(self._shadow)
        self._style(False)

    def _style(self, hover: bool) -> None:
        bg = "rgba(18, 29, 46, 0.84)" if hover else "rgba(18, 29, 46, 0.72)"
        border = "rgba(226,118,79,0.42)" if hover else Theme.line
        self.setStyleSheet(
            f"""
            QFrame#glassCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {self.radius}px;
                padding: {self.padding}px;
            }}
            """
        )

    def enterEvent(self, event) -> None:
        self._style(True)
        self._animate_shadow(self._hover_blur)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._style(False)
        self._animate_shadow(self._base_blur)
        super().leaveEvent(event)

    def _animate_shadow(self, radius: int) -> None:
        animation = QPropertyAnimation(self._shadow, b"blurRadius", self)
        animation.setDuration(Theme.motion.hover)
        animation.setEndValue(radius)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class FrostPanel(GlassCard):
    def __init__(self, parent=None, radius: int | None = None, padding: int = 0):
        super().__init__(parent=parent, radius=radius or Theme.radii.xl, padding=padding, elevated=True)
        self.setObjectName("frostPanel")
        self.setStyleSheet(
            f"""
            QFrame#frostPanel {{
                background-color: rgba(18, 29, 46, 0.76);
                border: 1px solid {Theme.line};
                border-radius: {self.radius}px;
                padding: {self.padding}px;
            }}
            """
        )


class StatusCard(GlassCard):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent=parent, radius=Theme.radii.md, padding=0, elevated=False)
        self.setProperty("title", title)
