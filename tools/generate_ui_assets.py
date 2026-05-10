from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient


def generate_placeholder_assets(target_root: Path) -> None:
    target_root.mkdir(parents=True, exist_ok=True)
    image = QImage(1600, 900, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor("#030915"))

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    gradient = QLinearGradient(0, 0, 0, image.height())
    gradient.setColorAt(0.0, QColor("#081426"))
    gradient.setColorAt(1.0, QColor("#02060F"))
    painter.fillRect(image.rect(), gradient)

    radial = QRadialGradient(QPointF(image.width() * 0.62, image.height() * 0.55), image.width() * 0.28)
    radial.setColorAt(0.0, QColor(242, 187, 150, 88))
    radial.setColorAt(0.35, QColor(242, 187, 150, 28))
    radial.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.fillRect(image.rect(), radial)

    pen = QPen(QColor(191, 213, 229, 36))
    pen.setWidthF(1.0)
    painter.setPen(pen)
    center = QPointF(image.width() * 0.62, image.height() * 0.58)
    for radius in (120, 180, 250, 340):
        painter.drawEllipse(center, radius, radius * 0.62)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(250, 212, 185, 160))
    painter.drawEllipse(QRectF(center.x() - 12, center.y() - 12, 24, 24))

    path = QPainterPath()
    path.moveTo(image.width() * 0.18, image.height() * 0.78)
    path.cubicTo(
        image.width() * 0.28,
        image.height() * 0.62,
        image.width() * 0.42,
        image.height() * 0.9,
        image.width() * 0.58,
        image.height() * 0.72,
    )
    painter.setPen(QPen(QColor(242, 187, 150, 52), 1.4))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)

    painter.end()
    image.save(str(target_root / "generated_background.png"))


if __name__ == "__main__":
    generate_placeholder_assets(Path(__file__).resolve().parents[1] / "resources" / "generated")
