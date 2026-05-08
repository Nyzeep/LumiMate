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
        self._shadow.setBlurRadius(34)
        self._shadow.setOffset(0, 14)
        self._shadow.setColor(Theme.shadow)
        self.setGraphicsEffect(self._shadow)
        bg = Theme.panel_warm if warm else Theme.panel_dark
        text = Theme.text_dark if warm else Theme.text
        border = "rgba(255,255,255,0.26)" if warm else "rgba(255,255,255,0.12)"
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
        self._shadow.setBlurRadius(22)
        self._shadow.setOffset(0, 8)
        self._shadow.setColor(QColor(5, 18, 30, 60))
        self.setGraphicsEffect(self._shadow)
        self._style()

    @pyqtProperty(float)
    def hover(self) -> float:
        return self._hover

    @hover.setter
    def hover(self, value: float) -> None:
        self._hover = value
        self._shadow.setBlurRadius(22 + int(value * 14))
        self._shadow.setColor(QColor(5, 18, 30, 60 + int(value * 35)))
        self._style()

    def _style(self) -> None:
        alpha = 0.15 + self._hover * 0.07
        border = 0.13 + self._hover * 0.11
        self.setText(f"{self.title}\n{self.subtitle}" if self.subtitle else self.title)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(239, 246, 248, {alpha:.3f});
                border: 1px solid rgba(255, 255, 255, {border:.3f});
                border-radius: 24px;
                padding: 11px 18px;
                color: {Theme.text};
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: white;
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
        bg.setColorAt(0.0, QColor(13, 38, 58, 112))
        bg.setColorAt(0.52, QColor(222, 216, 214, 56))
        bg.setColorAt(1.0, QColor(244, 226, 214, 90))
        painter.fillRect(self.rect(), bg)

        self._paint_moon(painter, w, h)
        self._paint_steps(painter, w, h)
        self._paint_geometry(painter, w, h)
        self._paint_character(painter, w, h)
        self._paint_flowers(painter, w, h)

    def _paint_moon(self, painter: QPainter, w: int, h: int) -> None:
        center = QPointF(w * (0.56 if self.mode != "chat" else 0.68), h * 0.43)
        radius = min(w, h) * (0.23 if self.mode == "companion" else 0.19)
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, QColor(255, 246, 235, 210))
        gradient.setColorAt(0.68, QColor(245, 226, 211, 118))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(center, radius, radius)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 56), 1))
        painter.drawEllipse(center, radius * 1.38, radius * 1.38)
        painter.drawArc(QRectF(center.x() - radius * 1.85, center.y() - radius * 1.4, radius * 3.7, radius * 2.8), 18 * 16, 235 * 16)

    def _paint_steps(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(14, 44, 66, 116))
        base_y = h * 0.80
        for i in range(9):
            x = w * (0.16 + i * 0.038)
            y = base_y - i * h * 0.033
            painter.drawRect(QRectF(x, y, w * 0.36, h * 0.035))
        painter.setBrush(QColor(229, 219, 213, 120))
        painter.drawRect(QRectF(w * 0.47, h * 0.22, w * 0.036, h * 0.50))
        painter.drawRect(QRectF(w * 0.53, h * 0.12, w * 0.030, h * 0.56))

    def _paint_geometry(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(QPen(QColor(255, 255, 255, 38), 1))
        for x in (0.20, 0.36, 0.78):
            xx = w * x + math.sin(self._phase + x) * 4
            painter.drawLine(QPointF(xx, h * 0.06), QPointF(xx, h * 0.94))
        for i in range(5):
            y = h * (0.18 + i * 0.15)
            painter.drawLine(QPointF(w * 0.08, y), QPointF(w * 0.92, y))

    def _paint_character(self, painter: QPainter, w: int, h: int) -> None:
        x = w * (0.47 if self.mode != "chat" else 0.74)
        y = h * 0.61 + math.sin(self._phase * 2.0) * 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(20, 50, 70, 210))
        body = QPainterPath()
        body.moveTo(x, y - h * 0.11)
        body.cubicTo(x - w * 0.055, y + h * 0.03, x - w * 0.040, y + h * 0.18, x - w * 0.11, y + h * 0.24)
        body.lineTo(x + w * 0.10, y + h * 0.24)
        body.cubicTo(x + w * 0.035, y + h * 0.10, x + w * 0.045, y - h * 0.02, x, y - h * 0.11)
        painter.drawPath(body)
        painter.setBrush(QColor(29, 78, 102, 226))
        painter.drawEllipse(QPointF(x, y - h * 0.17), w * 0.035, w * 0.035)
        painter.setBrush(QColor(199, 149, 166, 150))
        painter.drawEllipse(QPointF(x + w * 0.035, y - h * 0.14), w * 0.027, w * 0.020)

    def _paint_flowers(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(QPen(QColor(112, 126, 136, 96), 1))
        root = QPointF(w * 0.12, h * 0.86)
        for i in range(10):
            angle = -1.35 + i * 0.15
            length = h * (0.12 + i * 0.012)
            end = QPointF(root.x() + math.cos(angle) * length, root.y() + math.sin(angle) * length)
            painter.drawLine(root, end)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(201, 149, 166, 122))
            painter.drawEllipse(end, 4 + i % 3, 4 + i % 3)
            painter.setPen(QPen(QColor(112, 126, 136, 96), 1))


class SceneCard(PoeticPanel):
    def __init__(self, title: str, value: str, detail: str = "", parent=None, warm: bool = False):
        super().__init__(parent=parent, warm=warm, radius=28)
        self.warm = warm
        self.setMinimumHeight(104)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(7)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {Theme.dim if warm else Theme.muted}; font-size: 12px; font-weight: 600;")
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Microsoft YaHei UI", 17, QFont.Weight.DemiBold))
        self.value_label.setStyleSheet(f"color: {Theme.text_dark if warm else Theme.text};")
        self.detail_label = QLabel(detail)
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet(f"color: {Theme.dim if warm else Theme.muted}; font-size: 12px;")
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
