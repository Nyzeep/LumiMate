from __future__ import annotations

import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

from ui.themes import Theme


class DreamscapeBackground(QWidget):
    """A low-frequency painted atmosphere inspired by watercolor game UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._phase = 0.0
        self._dust = [
            (random.random(), random.random(), random.uniform(0.35, 1.2), random.random() * 6.28)
            for _ in range(42)
        ]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(Theme.motion.ambient_tick)

    def _tick(self) -> None:
        self._phase += 0.0045
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        w = max(rect.width(), 1)
        h = max(rect.height(), 1)

        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor("#081827"))
        base.setColorAt(0.34, QColor("#132F47"))
        base.setColorAt(0.67, QColor("#D9D3D1"))
        base.setColorAt(1.0, QColor("#F0E1D5"))
        painter.fillRect(rect, base)

        self._fog(painter, 0.32, 0.26, "#89AFC0", 58, 0.52, 0.0)
        self._fog(painter, 0.70, 0.28, "#EBD8C9", 96, 0.42, 1.3)
        self._fog(painter, 0.62, 0.76, "#B6A8C8", 55, 0.48, 2.4)

        painter.setPen(QPen(QColor(255, 255, 255, 34), 1))
        for x in (0.23, 0.39, 0.71, 0.88):
            xx = int(x * w + math.sin(self._phase + x) * 4)
            painter.drawLine(xx, 0, xx, h)
        for y in (0.18, 0.82):
            yy = int(y * h)
            painter.drawLine(0, yy, w, yy)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 246, 235, 138))
        moon_radius = min(w, h) * 0.18
        moon_center = QPointF(w * 0.55, h * 0.43)
        painter.drawEllipse(moon_center, moon_radius, moon_radius)
        painter.setBrush(QColor(255, 255, 255, 18))
        painter.drawEllipse(moon_center, moon_radius * 1.44, moon_radius * 1.44)

        self._paint_architecture(painter, w, h)
        self._paint_flora(painter, w, h)
        self._paint_dust(painter, w, h)

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
        painter.setBrush(QColor(21, 48, 69, 118))
        painter.drawRect(QRectF(w * 0.19, h * 0.67, w * 0.28, h * 0.26))
        painter.setBrush(QColor(230, 220, 214, 136))
        painter.drawRect(QRectF(w * 0.43, h * 0.28, w * 0.035, h * 0.41))
        painter.drawRect(QRectF(w * 0.49, h * 0.17, w * 0.032, h * 0.50))
        painter.setPen(QPen(QColor(255, 255, 255, 72), 1))
        painter.drawEllipse(QPointF(w * 0.49, h * 0.17), 7, 7)
        painter.drawArc(QRectF(w * 0.32, h * 0.25, w * 0.38, h * 0.48), 20 * 16, 250 * 16)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(12, 37, 56, 94))
        step_h = h * 0.026
        for i in range(8):
            painter.drawRect(QRectF(w * (0.16 + i * 0.025), h * (0.86 - i * 0.032), w * 0.25, step_h))

    def _paint_flora(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(QPen(QColor(116, 129, 138, 86), 1))
        root = QPointF(w * 0.11, h * 0.86)
        for i in range(12):
            angle = -1.45 + i * 0.16
            length = h * (0.12 + 0.035 * math.sin(i))
            end = QPointF(root.x() + math.cos(angle) * length, root.y() + math.sin(angle) * length)
            painter.drawLine(root, end)
            painter.setBrush(QColor(201, 149, 166, 110))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(end, 5 + i % 3, 5 + i % 3)
            painter.setPen(QPen(QColor(116, 129, 138, 86), 1))

    def _paint_dust(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        for x, y, size, seed in self._dust:
            drift_x = math.sin(self._phase + seed) * 5
            drift_y = math.cos(self._phase * 0.8 + seed) * 4
            alpha = int(28 + 22 * math.sin(seed + self._phase * 1.4))
            painter.setBrush(QColor(255, 246, 235, max(10, alpha)))
            painter.drawEllipse(QPointF(x * w + drift_x, y * h + drift_y), size, size)
