from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QPointF, QRectF, Qt, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.themes import Theme


class PoeticPanel(QFrame):
    def __init__(self, parent=None, warm: bool = False, radius: int | None = None):
        super().__init__(parent)
        self.radius = radius or Theme.radii.lg
        self.warm = warm
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("poeticPanel")
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(28)
        self._shadow.setOffset(0, 12)
        self._shadow.setColor(Theme.shadow)
        self.setGraphicsEffect(self._shadow)
        bg = Theme.panel_warm if warm else Theme.panel_dark
        text = Theme.text
        border = "rgba(180,204,228,0.22)" if warm else "rgba(180,204,228,0.16)"
        self.setStyleSheet(
            f"""
            QFrame#poeticPanel {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {self.radius}px;
                color: {text};
            }}
            """
        )


class QuietActionButton(QPushButton):
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self._hover = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(74)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(18)
        self._shadow.setOffset(0, 8)
        self._shadow.setColor(QColor(0, 0, 0, 92))
        self.setGraphicsEffect(self._shadow)
        self._style()

    @pyqtProperty(float)
    def hover(self) -> float:
        return self._hover

    @hover.setter
    def hover(self, value: float) -> None:
        self._hover = value
        self._shadow.setBlurRadius(18 + int(value * 12))
        self._shadow.setColor(QColor(0, 0, 0, 92 + int(value * 35)))
        self._style()

    def _style(self) -> None:
        alpha = 0.76 + self._hover * 0.06
        border = 0.16 + self._hover * 0.18
        self.setText(f"{self.title}\n{self.subtitle}" if self.subtitle else self.title)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(18, 29, 46, {alpha:.3f});
                border: 1px solid rgba(180, 204, 228, {border:.3f});
                border-radius: 18px;
                padding: 13px 18px;
                color: {Theme.text};
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: white;
                border-color: rgba(226, 118, 79, 0.55);
            }}
            QPushButton:pressed {{
                padding-top: 12px;
                padding-bottom: 10px;
            }}
            QPushButton:disabled {{
                color: rgba(238,243,245,0.38);
                background-color: rgba(239,246,248,0.07);
            }}
            """
        )

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


class BreathingLabel(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._opacity = 0.76
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._phase = 0.0
        self._timer.start(90)

    @pyqtProperty(float)
    def softOpacity(self) -> float:
        return self._opacity

    @softOpacity.setter
    def softOpacity(self, value: float) -> None:
        self._opacity = value
        self.setStyleSheet(f"color: rgba(238, 243, 245, {value:.3f});")

    def _tick(self) -> None:
        self._phase += 0.035
        self.softOpacity = 0.70 + math.sin(self._phase) * 0.16


class CompanionScene(QWidget):
    def __init__(self, mode: str = "home", parent=None):
        super().__init__(parent)
        self.mode = mode
        self._phase = 0.0
        self.setMinimumHeight(320)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(100)

    def _tick(self) -> None:
        self._phase += 0.006
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(self.width(), 1)
        h = max(self.height(), 1)

        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0, QColor(5, 12, 23, 170))
        bg.setColorAt(0.52, QColor(11, 25, 42, 152))
        bg.setColorAt(1.0, QColor(28, 43, 64, 132))
        painter.fillRect(self.rect(), bg)

        self._paint_moon(painter, w, h)
        self._paint_steps(painter, w, h)
        self._paint_geometry(painter, w, h)
        self._paint_character(painter, w, h)
        self._paint_flowers(painter, w, h)
        self._paint_scene_sparks(painter, w, h)

    def _paint_moon(self, painter: QPainter, w: int, h: int) -> None:
        center = QPointF(w * (0.62 if self.mode != "chat" else 0.68), h * 0.42)
        radius = min(w, h) * (0.31 if self.mode == "companion" else 0.25)
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, QColor(244, 231, 214, 178))
        gradient.setColorAt(0.68, QColor(183, 216, 232, 72))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(center, radius, radius)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(183, 216, 232, 62), 1))
        painter.drawEllipse(center, radius * 1.38, radius * 1.38)
        painter.drawArc(QRectF(center.x() - radius * 1.85, center.y() - radius * 1.4, radius * 3.7, radius * 2.8), 18 * 16, 235 * 16)

    def _paint_steps(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(3, 9, 18, 150))
        base_y = h * 0.84
        for i in range(10):
            x = w * (0.12 + i * 0.034)
            y = base_y - i * h * 0.031
            painter.drawRect(QRectF(x, y, w * 0.42, h * 0.030))
        painter.setBrush(QColor(183, 216, 232, 52))
        painter.drawRect(QRectF(w * 0.43, h * 0.18, w * 0.030, h * 0.56))
        painter.drawRect(QRectF(w * 0.52, h * 0.10, w * 0.026, h * 0.64))

    def _paint_geometry(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(QPen(QColor(180, 204, 228, 34), 1))
        for x in (0.18, 0.36, 0.70, 0.86):
            xx = w * x + math.sin(self._phase + x) * 4
            painter.drawLine(QPointF(xx, h * 0.06), QPointF(xx, h * 0.94))
        for i in range(5):
            y = h * (0.18 + i * 0.15)
            painter.drawLine(QPointF(w * 0.08, y), QPointF(w * 0.92, y))

    def _paint_character(self, painter: QPainter, w: int, h: int) -> None:
        x = w * (0.47 if self.mode != "chat" else 0.72)
        y = h * 0.62 + math.sin(self._phase * 2.0) * 3
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(5, 13, 24, 232))
        body = QPainterPath()
        body.moveTo(x, y - h * 0.15)
        body.cubicTo(x - w * 0.072, y + h * 0.02, x - w * 0.054, y + h * 0.20, x - w * 0.14, y + h * 0.29)
        body.lineTo(x + w * 0.13, y + h * 0.29)
        body.cubicTo(x + w * 0.050, y + h * 0.12, x + w * 0.060, y - h * 0.02, x, y - h * 0.15)
        painter.drawPath(body)
        painter.setBrush(QColor(28, 64, 91, 235))
        painter.drawEllipse(QPointF(x, y - h * 0.23), w * 0.050, w * 0.050)
        painter.setBrush(QColor(226, 118, 79, 170))
        painter.drawEllipse(QPointF(x + w * 0.048, y - h * 0.20), w * 0.034, w * 0.026)

    def _paint_flowers(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(QPen(QColor(119, 134, 154, 118), 1))
        root = QPointF(w * 0.10, h * 0.88)
        for i in range(14):
            angle = -1.44 + i * 0.13
            length = h * (0.18 + i * 0.014)
            end = QPointF(root.x() + math.cos(angle) * length, root.y() + math.sin(angle) * length)
            painter.drawLine(root, end)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(226, 118, 79, 132))
            painter.drawEllipse(end, 6 + i % 4, 6 + i % 4)
            painter.setPen(QPen(QColor(119, 134, 154, 118), 1))

    def _paint_scene_sparks(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(18):
            x = ((i * 0.173 + 0.07) % 1.0) * w + math.sin(self._phase + i) * 8
            y = ((i * 0.311 + 0.12) % 1.0) * h + math.cos(self._phase * 0.8 + i) * 6
            size = 1.5 + (i % 4) * 0.55
            painter.setBrush(QColor(236, 246, 252, 58 + (i % 5) * 10))
            painter.drawEllipse(QPointF(x, y), size, size)


class SceneCard(PoeticPanel):
    def __init__(self, title: str, value: str, detail: str = "", parent=None, warm: bool = False):
        super().__init__(parent=parent, warm=warm, radius=28)
        self.warm = warm
        self.setMinimumHeight(104)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(7)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {Theme.accent_soft if warm else Theme.muted}; font-size: 12px; font-weight: 700;")
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Microsoft YaHei UI", 17, QFont.Weight.DemiBold))
        self.value_label.setStyleSheet(f"color: {Theme.text};")
        self.detail_label = QLabel(detail)
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet(f"color: {Theme.muted}; font-size: 12px;")
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        if detail:
            layout.addWidget(self.detail_label)
        layout.addStretch()

    def set_value(self, value: str, detail: str | None = None) -> None:
        self.value_label.setText(value)
        if detail is not None:
            self.detail_label.setText(detail)
            if self.detail_label.parent() is None:
                self.layout().insertWidget(2, self.detail_label)
