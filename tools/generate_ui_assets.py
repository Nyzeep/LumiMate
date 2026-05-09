from __future__ import annotations

import math
from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resources" / "ui"


def _image(width: int, height: int) -> QImage:
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor(0, 0, 0, 0))
    return image


def _base_night(painter: QPainter, width: int, height: int) -> None:
    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0.00, QColor("#030817"))
    gradient.setColorAt(0.38, QColor("#071326"))
    gradient.setColorAt(0.72, QColor("#0D1A2D"))
    gradient.setColorAt(1.00, QColor("#152238"))
    painter.fillRect(0, 0, width, height, gradient)


def _fog(painter: QPainter, center: QPointF, radius: float, color: QColor) -> None:
    gradient = QRadialGradient(center, radius)
    center_color = QColor(color)
    mid_color = QColor(color)
    edge_color = QColor(color)
    mid_color.setAlpha(max(0, color.alpha() // 3))
    edge_color.setAlpha(0)
    gradient.setColorAt(0.0, center_color)
    gradient.setColorAt(0.55, mid_color)
    gradient.setColorAt(1.0, edge_color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawEllipse(center, radius, radius)


def _orbits(painter: QPainter, width: int, height: int, cx: float, cy: float, scale: float) -> None:
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for index, alpha in enumerate((58, 43, 31, 24)):
        pen = QPen(QColor(218, 227, 233, alpha), 1)
        painter.setPen(pen)
        radius = scale * (0.90 + index * 0.28)
        rect = QRectF(cx - radius, cy - radius * 0.76, radius * 2.0, radius * 1.52)
        painter.drawArc(rect, (12 + index * 7) * 16, (235 - index * 16) * 16)
    painter.setPen(Qt.PenStyle.NoPen)
    for angle, distance, size, alpha in ((22, 1.34, 5, 160), (112, 1.12, 4, 120), (198, 1.52, 6, 150)):
        rad = math.radians(angle)
        painter.setBrush(QColor(241, 196, 174, alpha))
        painter.drawEllipse(QPointF(cx + math.cos(rad) * scale * distance, cy + math.sin(rad) * scale * 0.72 * distance), size, size)


def _architecture(painter: QPainter, width: int, height: int) -> None:
    base_y = height * 0.76
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(5, 11, 23, 205))
    for index in range(10):
        painter.drawRect(QRectF(width * (0.23 + index * 0.033), base_y - index * height * 0.030, width * 0.34, height * 0.028))

    painter.setBrush(QColor(8, 15, 29, 226))
    painter.drawRect(QRectF(width * 0.56, height * 0.44, width * 0.055, height * 0.31))
    painter.drawRect(QRectF(width * 0.65, height * 0.34, width * 0.058, height * 0.42))
    painter.drawRect(QRectF(width * 0.73, height * 0.41, width * 0.050, height * 0.35))

    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor(226, 207, 189, 74), 3))
    painter.drawArc(QRectF(width * 0.608, height * 0.43, width * 0.084, height * 0.20), 0, 180 * 16)
    painter.drawLine(QPointF(width * 0.608, height * 0.53), QPointF(width * 0.608, height * 0.75))
    painter.drawLine(QPointF(width * 0.692, height * 0.53), QPointF(width * 0.692, height * 0.75))
    painter.drawArc(QRectF(width * 0.722, height * 0.48, width * 0.072, height * 0.16), 0, 180 * 16)


def _lumi_figure(painter: QPainter, x: float, y: float, scale: float, accent: QColor) -> None:
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(8, 14, 27, 240))
    body = QPainterPath()
    body.moveTo(x, y - 70 * scale)
    body.cubicTo(x - 47 * scale, y - 10 * scale, x - 38 * scale, y + 58 * scale, x - 86 * scale, y + 100 * scale)
    body.lineTo(x + 78 * scale, y + 100 * scale)
    body.cubicTo(x + 38 * scale, y + 46 * scale, x + 44 * scale, y - 8 * scale, x, y - 70 * scale)
    painter.drawPath(body)
    painter.setBrush(QColor(28, 49, 72, 238))
    painter.drawEllipse(QPointF(x, y - 104 * scale), 27 * scale, 31 * scale)
    painter.setBrush(accent)
    painter.drawEllipse(QPointF(x + 29 * scale, y - 83 * scale), 17 * scale, 13 * scale)
    painter.setPen(QPen(QColor(238, 219, 198, 126), max(1, int(2 * scale))))
    painter.drawLine(QPointF(x - 16 * scale, y - 18 * scale), QPointF(x - 54 * scale, y + 32 * scale))
    painter.drawLine(QPointF(x + 14 * scale, y - 15 * scale), QPointF(x + 43 * scale, y + 33 * scale))


def _flowers(painter: QPainter, root: QPointF, scale: float) -> None:
    for index in range(18):
        angle = -1.55 + index * 0.115
        length = scale * (70 + index * 5.4)
        end = QPointF(root.x() + math.cos(angle) * length, root.y() + math.sin(angle) * length)
        painter.setPen(QPen(QColor(124, 139, 158, 105), max(1, int(scale * 0.55))))
        painter.drawLine(root, end)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(230, 133, 96, 122))
        size = scale * (4.0 + index % 4)
        painter.drawEllipse(end, size, size)


def create_home_stage() -> None:
    width, height = 1800, 1080
    image = _image(width, height)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _base_night(painter, width, height)
    _fog(painter, QPointF(width * 0.61, height * 0.43), width * 0.28, QColor(238, 182, 154, 112))
    _fog(painter, QPointF(width * 0.42, height * 0.25), width * 0.42, QColor(39, 82, 122, 76))
    _fog(painter, QPointF(width * 0.82, height * 0.70), width * 0.36, QColor(13, 29, 52, 160))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(241, 214, 195, 185))
    painter.drawEllipse(QPointF(width * 0.62, height * 0.46), width * 0.135, width * 0.135)
    painter.setBrush(QColor(41, 49, 78, 120))
    painter.drawPie(QRectF(width * 0.62, height * 0.325, width * 0.27, width * 0.27), 270 * 16, 90 * 16)
    _orbits(painter, width, height, width * 0.59, height * 0.44, width * 0.22)
    _architecture(painter, width, height)
    _lumi_figure(painter, width * 0.46, height * 0.64, 1.22, QColor(230, 126, 90, 160))
    _flowers(painter, QPointF(width * 0.31, height * 0.82), 1.28)
    painter.setPen(QPen(QColor(190, 212, 225, 33), 1))
    for x in (0.18, 0.42, 0.67, 0.86):
        painter.drawLine(QPointF(width * x, 0), QPointF(width * x, height))
    painter.end()
    image.save(str(OUT / "lumi_home_stage.png"))


def create_companion_portrait() -> None:
    width, height = 1300, 1600
    image = _image(width, height)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _base_night(painter, width, height)
    _fog(painter, QPointF(width * 0.52, height * 0.38), width * 0.44, QColor(244, 213, 188, 104))
    _fog(painter, QPointF(width * 0.22, height * 0.20), width * 0.48, QColor(48, 86, 128, 90))
    _orbits(painter, width, height, width * 0.50, height * 0.39, width * 0.29)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(241, 214, 195, 170))
    painter.drawEllipse(QPointF(width * 0.51, height * 0.37), width * 0.16, width * 0.16)
    _architecture(painter, width, height)
    _lumi_figure(painter, width * 0.50, height * 0.61, 1.85, QColor(230, 126, 90, 170))
    painter.setPen(QPen(QColor(226, 207, 189, 42), 1))
    for y in (0.22, 0.38, 0.61, 0.78):
        painter.drawLine(QPointF(width * 0.08, height * y), QPointF(width * 0.92, height * y))
    painter.end()
    image.save(str(OUT / "lumi_companion_portrait.png"))


def create_atmosphere_texture() -> None:
    width, height = 1200, 900
    image = _image(width, height)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.fillRect(0, 0, width, height, QColor(3, 8, 18, 30))
    for index in range(640):
        x = (index * 97 % width) + math.sin(index) * 3
        y = (index * 193 % height) + math.cos(index * 0.7) * 3
        radius = 0.7 + (index % 7) * 0.23
        alpha = 10 + index % 38
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(226, 236, 244, alpha))
        painter.drawEllipse(QPointF(x, y), radius, radius)
    for index, color in enumerate((QColor(231, 139, 100, 34), QColor(93, 132, 174, 42), QColor(240, 222, 202, 25))):
        _fog(painter, QPointF(width * (0.24 + index * 0.24), height * (0.72 - index * 0.18)), width * (0.32 + index * 0.06), color)
    painter.end()
    image.save(str(OUT / "lumi_atmosphere_texture.png"))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    create_home_stage()
    create_companion_portrait()
    create_atmosphere_texture()


if __name__ == "__main__":
    main()
