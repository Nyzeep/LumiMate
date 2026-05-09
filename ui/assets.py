from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QPixmap


class LumiAssetManager:
    """Centralized project asset lookup for UI image resources."""

    _root = Path(__file__).resolve().parents[1] / "resources" / "ui"
    _cache: dict[str, QPixmap] = {}

    @classmethod
    def path(cls, name: str) -> Path:
        return cls._root / name

    @classmethod
    def pixmap(cls, name: str) -> QPixmap:
        if name not in cls._cache:
            cls._cache[name] = QPixmap(str(cls.path(name)))
        return cls._cache[name]

    @classmethod
    def exists(cls, name: str) -> bool:
        return cls.path(name).exists()
