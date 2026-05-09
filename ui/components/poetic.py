from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.animations import AmbientClock
from ui.assets import LumiAssetManager
from ui.components.geometric import OrbitalNodeButton, SpatialPanel
from ui.themes import Theme


class PoeticPanel(SpatialPanel):
    def __init__(self, parent=None, warm: bool = False, radius: int | None = None):
        super().__init__(parent=parent, warm=warm, radius=radius)


class QuietActionButton(OrbitalNodeButton):
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(title, "orbit", subtitle=subtitle, parent=parent, node_size=62)


class BreathingLabel(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._opacity = 0.76
        self._phase = 0.0
        AmbientClock.instance().tick.connect(self._tick)

    @pyqtProperty(float)
    def softOpacity(self) -> float:
        return self._opacity

    @softOpacity.setter
    def softOpacity(self, value: float) -> None:
        self._opacity = value
        self.setStyleSheet(f"color: rgba(242, 237, 229, {value:.3f});")

    def _tick(self, phase: float) -> None:
        self._phase = phase
        self.softOpacity = 0.68 + math.sin(self._phase * 1.4) * 0.13


class CompanionScene(QWidget):
    def __init__(self, mode: str = "home", parent=None):
        super().__init__(parent)
        self.mode = mode
        self._phase = 0.0
        self.setMinimumHeight(320)
        AmbientClock.instance().tick.connect(self._tick)

    def _tick(self, phase: float) -> None:
        self._phase = phase
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(self.width(), 1)
        h = max(self.height(), 1)
        self._paint_asset(painter, w, h)
        self._paint_lighting(painter, w, h)
        self._paint_geometry(painter, w, h)
        if self.mode in {"workbench", "settings"}:
            self._paint_ritual_core(painter, w, h)

    def _paint_asset(self, painter: QPainter, w: int, h: int) -> None:
        name = "lumi_companion_portrait.png" if self.mode == "companion" else "lumi_home_stage.png"
        pixmap = LumiAssetManager.pixmap(name)
        if pixmap.isNull():
            gradient = QLinearGradient(0, 0, w, h)
            gradient.setColorAt(0, QColor("#071120"))
            gradient.setColorAt(1, QColor("#152238"))
            painter.fillRect(self.rect(), gradient)
            return
        scaled = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        x = (w - scaled.width()) // 2
        y = (h - scaled.height()) // 2
        if self.mode == "chat":
            x = min(0, x - int(w * 0.10))
        painter.drawPixmap(x, y, scaled)

    def _paint_lighting(self, painter: QPainter, w: int, h: int) -> None:
        veil = QLinearGradient(0, 0, w, h)
        veil.setColorAt(0.0, QColor(2, 7, 19, 40))
        veil.setColorAt(0.64, QColor(2, 7, 19, 6))
        veil.setColorAt(1.0, QColor(2, 7, 19, 118))
        painter.fillRect(self.rect(), veil)
        center = QPointF(w * (0.60 if self.mode != "companion" else 0.50), h * 0.42)
        radius = min(w, h) * (0.42 if self.mode != "workbench" else 0.30)
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0.0, QColor(243, 225, 206, 50))
        glow.setColorAt(0.55, QColor(217, 120, 85, 15))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(center, radius, radius)

    def _paint_geometry(self, painter: QPainter, w: int, h: int) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        center = QPointF(w * (0.58 if self.mode != "companion" else 0.50), h * 0.43)
        scale = min(w, h) * (0.32 if self.mode != "workbench" else 0.22)
        for index in range(4):
            painter.setPen(QPen(QColor(201, 217, 226, 34 - index * 5), 1))
            radius = scale * (0.94 + index * 0.31)
            painter.drawArc(
                QRectF(center.x() - radius, center.y() - radius * 0.72, radius * 2, radius * 1.44),
                int((self._phase * 12 + index * 24) % 360) * 16,
                (124 + index * 22) * 16,
            )
        painter.setPen(QPen(QColor(201, 217, 226, 24), 1))
        for x in (0.18, 0.42, 0.67, 0.86):
            xx = w * x + math.sin(self._phase + x) * 3
            painter.drawLine(QPointF(xx, h * 0.06), QPointF(xx, h * 0.94))
        for index in range(12):
            angle = self._phase * 0.8 + index * math.tau / 12
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(242, 196, 174, 96 if index % 3 == 0 else 48))
            painter.drawEllipse(QPointF(center.x() + math.cos(angle) * scale * 1.62, center.y() + math.sin(angle) * scale * 1.06), 2.5, 2.5)

    def _paint_ritual_core(self, painter: QPainter, w: int, h: int) -> None:
        center = QPointF(w * 0.50, h * 0.50)
        radius = min(w, h) * 0.16
        painter.setPen(Qt.PenStyle.NoPen)
        core = QRadialGradient(center, radius * 2.4)
        core.setColorAt(0.0, QColor(243, 225, 206, 135))
        core.setColorAt(0.35, QColor(217, 120, 85, 56))
        core.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(core)
        painter.drawEllipse(center, radius * 2.4, radius * 2.4)
        painter.setPen(QPen(QColor(243, 225, 206, 92), 1.4))
        path = QPainterPath()
        path.moveTo(center.x(), center.y() - radius)
        path.lineTo(center.x() - radius * 0.86, center.y() + radius * 0.56)
        path.lineTo(center.x() + radius * 0.86, center.y() + radius * 0.56)
        path.closeSubpath()
        painter.drawPath(path)


class SceneCard(PoeticPanel):
    def __init__(self, title: str, value: str, detail: str = "", parent=None, warm: bool = False):
        super().__init__(parent=parent, warm=warm, radius=Theme.radii.lg)
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
