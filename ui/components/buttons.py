from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, QSize, Qt, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QPushButton, QSizePolicy

from ui.animations import AmbientClock
from ui.themes import Theme


class AnimatedButton(QPushButton):
    def __init__(self, text: str = "", parent=None, primary: bool = False):
        super().__init__(text, parent)
        self.primary = primary
        self._glow = 0.0
        self._phase = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("QPushButton { background: transparent; border: 0; }")
        AmbientClock.instance().tick.connect(self._on_tick)

    @pyqtProperty(float)
    def glow(self) -> float:
        return self._glow

    @glow.setter
    def glow(self, value: float) -> None:
        self._glow = value
        self.update()

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(QFont(Theme.font_stack(), 10, QFont.Weight.DemiBold))
        return QSize(max(96, metrics.horizontalAdvance(self.text()) + 42), 44)

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

    def _on_tick(self, phase: float) -> None:
        self._phase = phase
        if self._glow > 0.01 or self.primary:
            self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        enabled = 1.0 if self.isEnabled() else 0.34
        center = QPointF(rect.left() + 18, rect.center().y())
        radius = 8 + self._glow * 2
        if self.primary:
            gradient = QRadialGradient(center, 26 + self._glow * 10)
            gradient.setColorAt(0.0, QColor(217, 120, 85, int((24 + self._glow * 18) * enabled)))
            gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawEllipse(center, 26 + self._glow * 10, 26 + self._glow * 10)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(201, 217, 226, int((34 + self._glow * 36) * enabled)), 1))
        painter.drawArc(QRectF(center.x() - radius, center.y() - radius * 0.72, radius * 2, radius * 1.44), int(self._phase * 12) * 16, int((140 + self._glow * 64) * 16))
        painter.setPen(QPen(QColor(217, 120, 85, int((98 + self._glow * 48) * enabled)), 1.1))
        angle = self._phase * 2.0
        painter.drawEllipse(QPointF(center.x() + math.cos(angle) * radius, center.y() + math.sin(angle) * radius), 2.8, 2.8)
        painter.setPen(QPen(QColor(201, 217, 226, int((28 + self._glow * 34) * enabled)), 1))
        painter.drawLine(QPointF(center.x() + radius + 6, center.y()), QPointF(center.x() + 18, center.y()))
        painter.setPen(QColor(242, 237, 229, int((144 + self._glow * 62) * enabled)))
        painter.setFont(QFont(Theme.font_stack(), 10, QFont.Weight.DemiBold))
        painter.drawText(QRectF(center.x() + 22, rect.top(), rect.width() - 26, rect.height()), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())


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
        self._phase = 0.0
        self._hover = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(QSize(104, 76))
        self.setToolTip(text)
        self.setStyleSheet("QPushButton { background: transparent; border: 0; }")
        AmbientClock.instance().tick.connect(self._on_tick)

    def set_expanded(self, expanded: bool) -> None:
        return

    def enterEvent(self, event) -> None:
        self._hover = 1.0
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = 0.0
        self.update()
        super().leaveEvent(event)

    def _on_tick(self, phase: float) -> None:
        self._phase = phase
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(4, 2, -4, -2)
        checked = self.isChecked()
        node = QPointF(rect.center().x(), rect.top() + 25)
        radius = 18
        alpha = 150 if checked else 80
        if checked or self._hover:
            glow = QRadialGradient(node, 42)
            glow.setColorAt(0.0, QColor(217, 120, 85, 34 if checked else 20))
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(node, 42, 42)
        painter.setPen(QPen(QColor(201, 217, 226, alpha), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(node, radius, radius)
        painter.drawArc(QRectF(node.x() - radius * 1.32, node.y() - radius * 0.88, radius * 2.64, radius * 1.76), int(self._phase * 18) * 16, 120 * 16)
        painter.setPen(QColor(243, 225, 206, 190 if checked else 128))
        painter.setFont(QFont(Theme.font_stack(), 13, QFont.Weight.DemiBold))
        painter.drawText(QRectF(node.x() - 18, node.y() - 12, 36, 24), Qt.AlignmentFlag.AlignCenter, self.icon)
        painter.setFont(QFont(Theme.font_stack(), 10))
        painter.setPen(QColor(242, 237, 229, 186 if checked else 118))
        painter.drawText(QRectF(rect.left(), rect.top() + 52, rect.width(), 20), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self.label)


SidebarButton = NavigationItem
