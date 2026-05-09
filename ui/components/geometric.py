from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, QSize, Qt, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QFrame, QPushButton, QSizePolicy, QWidget

from ui.animations import AmbientClock
from ui.themes import Theme


def _rgba(hex_color: str, alpha: int) -> QColor:
    color = QColor(hex_color)
    color.setAlpha(alpha)
    return color


class SpatialPanel(QFrame):
    def __init__(self, parent=None, warm: bool = False, radius: int | None = None):
        super().__init__(parent)
        self.warm = warm
        self.radius = radius or Theme.radii.lg
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self.warm:
            gradient.setColorAt(0.0, QColor(24, 28, 43, 96))
            gradient.setColorAt(0.58, QColor(7, 14, 27, 60))
            gradient.setColorAt(1.0, QColor(2, 7, 19, 24))
            line = QColor(242, 180, 140, 42)
        else:
            gradient.setColorAt(0.0, QColor(10, 20, 38, 78))
            gradient.setColorAt(0.60, QColor(4, 10, 21, 44))
            gradient.setColorAt(1.0, QColor(2, 7, 19, 18))
            line = QColor(201, 217, 226, 30)
        painter.fillPath(path, gradient)
        painter.setPen(QPen(line, 1))
        edge = 34
        painter.drawLine(QPointF(rect.left() + edge, rect.top()), QPointF(rect.left() + edge * 2.3, rect.top()))
        painter.drawLine(QPointF(rect.right() - edge * 2.0, rect.top()), QPointF(rect.right() - edge * 0.55, rect.top()))
        painter.drawLine(QPointF(rect.left(), rect.top() + edge), QPointF(rect.left(), rect.top() + edge * 2.2))
        painter.drawLine(QPointF(rect.right(), rect.bottom() - edge * 2.1), QPointF(rect.right(), rect.bottom() - edge * 0.7))
        painter.setPen(QPen(QColor(201, 217, 226, 12), 1))
        painter.drawLine(QPointF(rect.left() + 26, rect.top() + 38), QPointF(rect.right() - 26, rect.top() + 38))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(217, 120, 85, 56 if self.warm else 34))
        painter.drawEllipse(QPointF(rect.left() + edge, rect.top()), 2.2, 2.2)
        painter.drawEllipse(QPointF(rect.right() - edge * 0.55, rect.top()), 1.8, 1.8)
        super().paintEvent(event)


class OrbitalNodeButton(QPushButton):
    def __init__(self, label: str, symbol: str, subtitle: str = "", parent=None, node_size: int = 68):
        super().__init__(parent)
        self.label = label
        self.symbol = symbol
        self.subtitle = subtitle
        self.node_size = node_size
        self._hover = 0.0
        self._phase = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(max(148, node_size + 84), max(92, node_size + 30))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("QPushButton { background: transparent; border: 0; }")
        self.setToolTip(label)
        AmbientClock.instance().tick.connect(self._on_tick)

    @pyqtProperty(float)
    def hover(self) -> float:
        return self._hover

    @hover.setter
    def hover(self, value: float) -> None:
        self._hover = value
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(max(188, self.node_size + 116), max(104, self.node_size + 42))

    def enterEvent(self, event) -> None:
        self._animate(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate(0.0)
        super().leaveEvent(event)

    def _animate(self, target: float) -> None:
        animation = QPropertyAnimation(self, b"hover", self)
        animation.setDuration(Theme.motion.hover)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _on_tick(self, phase: float) -> None:
        self._phase = phase
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        enabled_alpha = 1.0 if self.isEnabled() else 0.36
        node_center = QPointF(rect.left() + self.node_size * 0.64, rect.center().y() - 4)
        radius = self.node_size * 0.42

        glow = QRadialGradient(node_center, radius * (2.0 + self._hover * 0.34))
        glow.setColorAt(0.0, QColor(217, 120, 85, int((18 + self._hover * 20) * enabled_alpha)))
        glow.setColorAt(0.44, QColor(184, 206, 217, int((8 + self._hover * 8) * enabled_alpha)))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(node_center, radius * 2.0, radius * 2.0)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        for index, scale in enumerate((1.0, 1.36, 1.78)):
            alpha = int((42 - index * 9 + self._hover * 28) * enabled_alpha)
            painter.setPen(QPen(QColor(201, 217, 226, alpha), 1))
            orbit = QRectF(node_center.x() - radius * scale, node_center.y() - radius * scale * 0.72, radius * 2 * scale, radius * 1.44 * scale)
            start = int((self._phase * (12 + index * 2) + index * 56) % 360) * 16
            painter.drawArc(orbit, start, int((70 + self._hover * 66) * 16))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(243, 225, 206, int((112 + self._hover * 44) * enabled_alpha)))
        painter.drawEllipse(node_center, radius * (0.18 + self._hover * 0.03), radius * (0.18 + self._hover * 0.03))
        painter.setBrush(QColor(217, 120, 85, int((116 + self._hover * 42) * enabled_alpha)))
        marker_angle = self._phase * 1.5
        painter.drawEllipse(
            QPointF(node_center.x() + math.cos(marker_angle) * radius * 1.28, node_center.y() + math.sin(marker_angle) * radius * 0.84),
            radius * 0.12,
            radius * 0.12,
        )
        for index in range(3):
            drift = self._phase * (0.9 + index * 0.18) + index * 1.7
            dot = QPointF(
                node_center.x() + math.cos(drift) * radius * (1.55 + index * 0.18),
                node_center.y() + math.sin(drift) * radius * (0.82 + index * 0.10),
            )
            painter.setBrush(QColor(242, 237, 229, int((34 + self._hover * 34) * enabled_alpha)))
            painter.drawEllipse(dot, 1.5, 1.5)
        self._paint_symbol(painter, node_center, radius, enabled_alpha)

        text_left = node_center.x() + radius * 1.55
        if rect.width() < 190:
            text_left = rect.left() + 4
        painter.setPen(QColor(242, 237, 229, int((116 + self._hover * 98) * enabled_alpha)))
        title_font = QFont(Theme.font_stack(), 12, QFont.Weight.DemiBold)
        painter.setFont(title_font)
        painter.drawLine(QPointF(node_center.x() + radius * 1.05, node_center.y()), QPointF(text_left - 8, node_center.y()))
        painter.drawText(QRectF(text_left, rect.center().y() - 23, rect.right() - text_left - 8, 24), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.label)
        if self.subtitle:
            painter.setPen(QColor(174, 184, 195, int((104 + self._hover * 50) * enabled_alpha)))
            painter.setFont(QFont(Theme.font_stack(), 9))
            metrics = QFontMetrics(painter.font())
            subtitle = metrics.elidedText(self.subtitle, Qt.TextElideMode.ElideRight, max(24, int(rect.right() - text_left - 8)))
            painter.drawText(QRectF(text_left, rect.center().y() + 3, rect.right() - text_left - 8, 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, subtitle)

    def _paint_symbol(self, painter: QPainter, center: QPointF, radius: float, enabled_alpha: float) -> None:
        pen = QPen(QColor(243, 225, 206, int((124 + self._hover * 70) * enabled_alpha)), 1.25)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        symbol = self.symbol.lower()
        if symbol in {"triangle", "home", "workbench"}:
            path = QPainterPath()
            path.moveTo(center.x(), center.y() - radius * 0.46)
            path.lineTo(center.x() - radius * 0.40, center.y() + radius * 0.34)
            path.lineTo(center.x() + radius * 0.40, center.y() + radius * 0.34)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(QPointF(center.x(), center.y() - radius * 0.28), QPointF(center.x(), center.y() + radius * 0.20))
        elif symbol in {"chat", "orbit"}:
            painter.drawEllipse(center, radius * 0.48, radius * 0.30)
            painter.drawLine(QPointF(center.x() - radius * 0.48, center.y()), QPointF(center.x() + radius * 0.48, center.y()))
            painter.drawEllipse(QPointF(center.x() - radius * 0.24, center.y()), radius * 0.055, radius * 0.055)
            painter.drawEllipse(QPointF(center.x() + radius * 0.24, center.y()), radius * 0.055, radius * 0.055)
        elif symbol in {"companion", "spark"}:
            painter.drawLine(QPointF(center.x(), center.y() - radius * 0.52), QPointF(center.x(), center.y() + radius * 0.52))
            painter.drawLine(QPointF(center.x() - radius * 0.52, center.y()), QPointF(center.x() + radius * 0.52, center.y()))
            painter.drawLine(QPointF(center.x() - radius * 0.30, center.y() - radius * 0.30), QPointF(center.x() + radius * 0.30, center.y() + radius * 0.30))
            painter.drawLine(QPointF(center.x() + radius * 0.30, center.y() - radius * 0.30), QPointF(center.x() - radius * 0.30, center.y() + radius * 0.30))
        elif symbol in {"settings", "ring"}:
            for i in range(6):
                angle = math.tau * i / 6
                painter.drawLine(
                    QPointF(center.x() + math.cos(angle) * radius * 0.30, center.y() + math.sin(angle) * radius * 0.30),
                    QPointF(center.x() + math.cos(angle) * radius * 0.52, center.y() + math.sin(angle) * radius * 0.52),
                )
            painter.drawEllipse(center, radius * 0.23, radius * 0.23)
        else:
            painter.drawEllipse(center, radius * 0.38, radius * 0.38)


class RitualProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self._state = "idle"
        self._message = "Lumi 正在安静等待"
        self._progress = 0.0
        self.setMinimumHeight(172)
        AmbientClock.instance().tick.connect(self._on_tick)

    def set_state(self, state: str, message: str, step: int | None = None, total: int | None = None) -> None:
        self._state = state
        self._message = message
        if step is not None and total:
            self._progress = max(0.0, min(1.0, step / max(total, 1)))
        elif state in {"ready", "running"}:
            self._progress = 1.0
        elif state == "idle":
            self._progress = 0.0
        self.update()

    def _on_tick(self, phase: float) -> None:
        self._phase = phase
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(6, 8, -6, -8)
        center = QPointF(rect.left() + min(rect.width() * 0.34, 190), rect.center().y() - 6)
        radius = min(rect.height() * 0.34, 64)

        glow = QRadialGradient(center, radius * 2.6)
        glow.setColorAt(0.0, QColor(217, 120, 85, 68))
        glow.setColorAt(0.48, QColor(184, 206, 217, 24))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(center, radius * 2.4, radius * 2.4)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        for index, scale in enumerate((1.0, 1.38, 1.78)):
            painter.setPen(QPen(QColor(201, 217, 226, 38 - index * 8), 1))
            orbit = QRectF(center.x() - radius * scale, center.y() - radius * scale, radius * 2 * scale, radius * 2 * scale)
            painter.drawEllipse(orbit)
        painter.setPen(QPen(QColor(217, 120, 85, 150), 2))
        painter.drawArc(QRectF(center.x() - radius * 1.42, center.y() - radius * 1.42, radius * 2.84, radius * 2.84), 90 * 16, -int(360 * self._progress) * 16)

        painter.setPen(Qt.PenStyle.NoPen)
        pulse = 0.76 + math.sin(self._phase * 2.8) * 0.20
        painter.setBrush(QColor(243, 225, 206, int(145 + 70 * pulse)))
        painter.drawEllipse(center, radius * 0.18, radius * 0.18)

        painter.setFont(QFont(Theme.font_stack(), 18, QFont.Weight.DemiBold))
        painter.setPen(QColor(242, 237, 229, 224))
        text_rect = QRectF(center.x() + radius * 2.0, rect.top() + 28, rect.width() - center.x() - radius * 1.6, 34)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Lumi 正在苏醒")
        painter.setFont(QFont(Theme.font_stack(), 10))
        painter.setPen(QColor(174, 184, 195, 174))
        painter.drawText(QRectF(text_rect.left(), text_rect.bottom() + 10, text_rect.width(), 52), Qt.TextFlag.TextWordWrap, self._message)

        labels = ("连接声音", "构筑记忆", "点亮语言", "校准呼吸")
        base_x = text_rect.left()
        base_y = rect.bottom() - 28
        span = max(46, min(118, (rect.right() - base_x - 20) / 4))
        for index, label in enumerate(labels):
            x = base_x + index * span
            active = self._progress >= (index + 1) / 4 or self._state == "running"
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(217, 120, 85, 170 if active else 66))
            painter.drawEllipse(QPointF(x, base_y), 4.0 if active else 3.0, 4.0 if active else 3.0)
            painter.setPen(QColor(242, 237, 229, 142 if active else 78))
            painter.drawText(QRectF(x + 10, base_y - 10, span - 12, 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)
