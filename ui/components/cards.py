from __future__ import annotations

from ui.components.geometric import SpatialPanel
from ui.themes import Theme


class GlassCard(SpatialPanel):
    def __init__(self, parent=None, radius: int | None = None, padding: int = 0, elevated: bool = True):
        super().__init__(parent=parent, warm=elevated, radius=radius or Theme.radii.lg)
        self.padding = padding


class FrostPanel(SpatialPanel):
    def __init__(self, parent=None, radius: int | None = None, padding: int = 0):
        super().__init__(parent=parent, warm=True, radius=radius or Theme.radii.xl)
        self.padding = padding


class StatusCard(GlassCard):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent=parent, radius=Theme.radii.md, padding=0, elevated=False)
        self.setProperty("title", title)
