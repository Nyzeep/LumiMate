from __future__ import annotations

import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

from ui.animations import AmbientClock
from ui.assets import LumiAssetManager
from ui.themes import Theme


class DreamscapeBackground(QWidget):
    """A cinematic nighttime atmosphere that breathes behind every space."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._phase = 0.0
        self._dust = [(random.random(), random.random(), random.uniform(0.6, 2.0), random.random() * 6.28) for _ in range(92)]
        self._clock = AmbientClock.instance()
        self._clock.tick.connect(self._tick)

    def _tick(self, phase: float) -> None:
        self._phase = phase
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        w = max(rect.width(), 1)
        h = max(rect.height(), 1)

        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor("#020713"))
        base.setColorAt(0.38, QColor("#071120"))
        base.setColorAt(0.72, QColor("#0B1728"))
        base.setColorAt(1.0, QColor("#152238"))
        painter.fillRect(rect, base)

        self._fog(painter, 0.17, 0.16, "#173F62", 72, 0.52, 0.0)
        self._fog(painter, 0.73, 0.28, "#294B68", 58, 0.42, 1.3)
        self._fog(painter, 0.62, 0.78, "#D97855", 38, 0.48, 2.4)
        self._fog(painter, 0.48, 0.50, "#B8CED9", 30, 0.36, 3.1)

        texture = LumiAssetManager.pixmap("lumi_atmosphere_texture.png")
        if not texture.isNull():
            painter.setOpacity(0.32)
            painter.drawPixmap(rect, texture)
            painter.setOpacity(1.0)

        painter.setPen(QPen(QColor(201, 217, 226, 20), 1))
        for x in (0.17, 0.39, 0.62, 0.84):
            xx = int(x * w + math.sin(self._phase + x) * 4)
            painter.drawLine(xx, 0, xx, h)
        for y in (0.21, 0.50, 0.83):
            yy = int(y * h)
            painter.drawLine(0, yy, w, yy)

        painter.setPen(Qt.PenStyle.NoPen)
        glow_radius = min(w, h) * 0.18
        glow_center = QPointF(w * 0.62, h * 0.40)
        moon_glow = QRadialGradient(glow_center, glow_radius * 1.8)
        moon_glow.setColorAt(0.0, QColor(243, 225, 206, 55))
        moon_glow.setColorAt(0.52, QColor(184, 206, 217, 18))
        moon_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(moon_glow)
        painter.drawEllipse(glow_center, glow_radius * 1.8, glow_radius * 1.8)

        self._paint_architecture(painter, w, h)
        self._paint_dust(painter, w, h)
        self._paint_orbits(painter, w, h)

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
        painter.setBrush(QColor(4, 10, 20, 82))
        painter.drawRect(QRectF(w * 0.00, h * 0.16, w, h * 0.09))
        painter.setBrush(QColor(18, 32, 52, 84))
        painter.drawRect(QRectF(w * 0.08, h * 0.74, w * 0.46, h * 0.17))
        painter.setBrush(QColor(184, 206, 217, 28))
        painter.drawRect(QRectF(w * 0.49, h * 0.26, w * 0.018, h * 0.50))
        painter.drawRect(QRectF(w * 0.58, h * 0.18, w * 0.015, h * 0.58))
        painter.setPen(QPen(QColor(217, 120, 85, 64), 1))
        painter.drawEllipse(QPointF(w * 0.51, h * 0.25), 5, 5)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(3, 9, 18, 90))
        step_h = h * 0.024
        for i in range(8):
            painter.drawRect(QRectF(w * (0.14 + i * 0.032), h * (0.91 - i * 0.032), w * 0.34, step_h))

    def _paint_dust(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        for x, y, size, seed in self._dust:
            drift_x = math.sin(self._phase + seed) * 7
            drift_y = math.cos(self._phase * 0.8 + seed) * 5
            alpha = int(26 + 28 * math.sin(seed + self._phase * 1.4))
            painter.setBrush(QColor(223, 238, 248, max(9, alpha)))
            painter.drawEllipse(QPointF(x * w + drift_x, y * h + drift_y), size, size)

    def _paint_orbits(self, painter: QPainter, w: int, h: int) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        center = QPointF(w * 0.61, h * 0.43)
        scale = min(w, h) * 0.28
        for i in range(5):
            alpha = 34 - i * 4
            painter.setPen(QPen(QColor(201, 217, 226, max(8, alpha)), 1))
            radius = scale * (0.8 + i * 0.22)
            start = int((self._phase * 9 + i * 19) % 360) * 16
            painter.drawArc(QRectF(center.x() - radius, center.y() - radius * 0.72, radius * 2, radius * 1.44), start, (118 + i * 22) * 16)
