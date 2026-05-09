from __future__ import annotations

import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

from ui.themes import Theme


class DreamscapeBackground(QWidget):
    """A low-frequency painted atmosphere for the Lumi console shell."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._phase = 0.0
        self._dust = [(random.random(), random.random(), random.uniform(0.7, 2.2), random.random() * 6.28) for _ in range(54)]
        self._flakes = [
            (random.random(), random.random(), random.uniform(7.0, 18.0), random.random() * 6.28, random.uniform(0.45, 1.0))
            for _ in range(34)
        ]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(Theme.motion.ambient_tick)

    def _tick(self) -> None:
        self._phase += 0.005
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        w = max(rect.width(), 1)
        h = max(rect.height(), 1)

        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor("#030814"))
        base.setColorAt(0.42, QColor("#07111F"))
        base.setColorAt(0.78, QColor("#0F1B2C"))
        base.setColorAt(1.0, QColor("#182337"))
        painter.fillRect(rect, base)

        self._fog(painter, 0.22, 0.18, "#15375A", 78, 0.45, 0.0)
        self._fog(painter, 0.76, 0.26, "#244A68", 66, 0.34, 1.3)
        self._fog(painter, 0.62, 0.80, "#E2764F", 30, 0.40, 2.4)
        self._fog(painter, 0.48, 0.50, "#B7D8E8", 28, 0.32, 3.1)

        painter.setPen(QPen(QColor(180, 204, 228, 24), 1))
        for x in (0.18, 0.39, 0.62, 0.83):
            xx = int(x * w + math.sin(self._phase + x) * 4)
            painter.drawLine(xx, 0, xx, h)
        for y in (0.18, 0.48, 0.82):
            yy = int(y * h)
            painter.drawLine(0, yy, w, yy)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(244, 231, 214, 96))
        moon_radius = min(w, h) * 0.16
        moon_center = QPointF(w * 0.70, h * 0.38)
        painter.drawEllipse(moon_center, moon_radius, moon_radius)
        painter.setBrush(QColor(183, 216, 232, 15))
        painter.drawEllipse(moon_center, moon_radius * 1.58, moon_radius * 1.58)

        self._paint_architecture(painter, w, h)
        self._paint_dust(painter, w, h)
        self._paint_snowflakes(painter, w, h)

    def _fog(self, painter: QPainter, x_ratio: float, y_ratio: float, color: str, alpha: int, radius_ratio: float, seed: float) -> None:
        w = max(self.width(), 1)
        h = max(self.height(), 1)
        x = (x_ratio + math.sin(self._phase + seed) * 0.018) * w
        y = (y_ratio + math.cos(self._phase * 0.7 + seed) * 0.022) * h
        radius = max(w, h) * radius_ratio
        gradient = QRadialGradient(QPointF(x, y), radius)
        center = QColor(color)
        center.setAlpha(alpha)
        middle = QColor(color)
        middle.setAlpha(alpha // 3)
        edge = QColor(color)
        edge.setAlpha(0)
        gradient.setColorAt(0.0, center)
        gradient.setColorAt(0.55, middle)
        gradient.setColorAt(1.0, edge)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(QPointF(x, y), radius, radius)

    def _paint_architecture(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(4, 10, 20, 112))
        painter.drawRect(QRectF(w * 0.00, h * 0.14, w, h * 0.10))
        painter.setBrush(QColor(18, 32, 52, 104))
        painter.drawRect(QRectF(w * 0.10, h * 0.70, w * 0.38, h * 0.20))
        painter.setBrush(QColor(183, 216, 232, 42))
        painter.drawRect(QRectF(w * 0.48, h * 0.24, w * 0.026, h * 0.52))
        painter.drawRect(QRectF(w * 0.56, h * 0.14, w * 0.021, h * 0.58))
        painter.setPen(QPen(QColor(226, 118, 79, 76), 1))
        painter.drawEllipse(QPointF(w * 0.51, h * 0.23), 6, 6)
        painter.drawArc(QRectF(w * 0.34, h * 0.26, w * 0.34, h * 0.46), 18 * 16, 250 * 16)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(3, 9, 18, 116))
        step_h = h * 0.024
        for i in range(8):
            painter.drawRect(QRectF(w * (0.13 + i * 0.029), h * (0.88 - i * 0.030), w * 0.30, step_h))

    def _paint_dust(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        for x, y, size, seed in self._dust:
            drift_x = math.sin(self._phase + seed) * 7
            drift_y = math.cos(self._phase * 0.8 + seed) * 5
            alpha = int(30 + 24 * math.sin(seed + self._phase * 1.4))
            painter.setBrush(QColor(223, 238, 248, max(12, alpha)))
            painter.drawEllipse(QPointF(x * w + drift_x, y * h + drift_y), size, size)

    def _paint_snowflakes(self, painter: QPainter, w: int, h: int) -> None:
        for x, y, size, seed, opacity in self._flakes:
            px = (x * w + math.sin(self._phase * 1.3 + seed) * 16) % max(w, 1)
            py = (y * h + math.cos(self._phase + seed) * 12) % max(h, 1)
            alpha = int(50 + 78 * opacity)
            painter.save()
            painter.translate(px, py)
            painter.rotate(math.degrees(seed + self._phase * 0.8))
            painter.setPen(QPen(QColor(236, 246, 252, alpha), 1))
            arm = size * 0.55
            branch = size * 0.20
            for angle in (0, 60, 120):
                painter.save()
                painter.rotate(angle)
                painter.drawLine(QPointF(-arm, 0), QPointF(arm, 0))
                painter.drawLine(QPointF(arm * 0.45, 0), QPointF(arm * 0.68, branch))
                painter.drawLine(QPointF(arm * 0.45, 0), QPointF(arm * 0.68, -branch))
                painter.drawLine(QPointF(-arm * 0.45, 0), QPointF(-arm * 0.68, branch))
                painter.drawLine(QPointF(-arm * 0.45, 0), QPointF(-arm * 0.68, -branch))
                painter.restore()
            painter.restore()
