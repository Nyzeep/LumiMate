from __future__ import annotations

from PyQt6.QtWidgets import QStackedWidget

from ui.animations import fade_in


class AnimatedStackWidget(QStackedWidget):
    def setCurrentIndex(self, index: int) -> None:
        if index == self.currentIndex():
            return
        super().setCurrentIndex(index)
        fade_in(self.currentWidget(), 300)
