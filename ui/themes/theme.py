from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtGui import QColor


@dataclass(frozen=True)
class Spacing:
    xs: int = 6
    sm: int = 10
    md: int = 16
    lg: int = 24
    xl: int = 36
    xxl: int = 52


@dataclass(frozen=True)
class Radii:
    sm: int = 10
    md: int = 18
    lg: int = 28
    xl: int = 36


@dataclass(frozen=True)
class Motion:
    hover: int = 520
    page: int = 680
    breath: int = 5200
    ambient_tick: int = 33


class Theme:
    ink = "#071120"
    ink_deep = "#020713"
    twilight = "#0B1728"
    midnight = "#0E1A2E"
    panel_blue = "#111E33"
    mist = "#DDE6ED"
    moon = "#F3E1CE"
    moon_soft = "#D7E3EC"
    accent = "#D97855"
    accent_soft = "#F1A47A"
    dusty_purple = "#9B9AB5"
    mist_blue = "#82A6BF"
    pale_cyan = "#B8CED9"
    flower = "#D97855"
    text = "#F2EDE5"
    text_dark = "#F2EDE5"
    muted = "#AEB8C3"
    dim = "#788798"
    line = "rgba(201, 217, 226, 0.16)"
    line_soft = "rgba(201, 217, 226, 0.08)"
    panel = "rgba(11, 20, 36, 0.58)"
    panel_warm = "rgba(20, 27, 42, 0.64)"
    panel_dark = "rgba(5, 12, 24, 0.58)"
    shadow = QColor(0, 0, 0, 115)

    spacing = Spacing()
    radii = Radii()
    motion = Motion()

    @classmethod
    def font_stack(cls) -> str:
        return '"HarmonyOS Sans SC", "Source Han Sans SC", "Microsoft YaHei UI", "Inter", "SF Pro Display", "Segoe UI"'

    @classmethod
    def app_qss(cls) -> str:
        return f"""
            * {{
                font-family: {cls.font_stack()};
                letter-spacing: 0px;
                color: {cls.text};
            }}
            QMainWindow, QWidget {{
                background: transparent;
            }}
            QLabel {{
                background: transparent;
            }}
            QToolTip {{
                color: {cls.text};
                background-color: rgba(5, 12, 24, 0.96);
                border: 1px solid rgba(217, 120, 85, 0.32);
                border-radius: 9px;
                padding: 7px 10px;
            }}
            QProgressBar {{
                min-height: 6px;
                max-height: 6px;
                border: 0;
                border-radius: 3px;
                background: rgba(201, 217, 226, 0.10);
                color: transparent;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.accent}, stop:0.62 {cls.accent_soft}, stop:1 {cls.pale_cyan});
            }}
            QSlider::groove:horizontal {{
                height: 5px;
                border-radius: 2px;
                background: rgba(201, 217, 226, 0.14);
            }}
            QSlider::sub-page:horizontal {{
                border-radius: 2px;
                background: rgba(217, 120, 85, 0.74);
            }}
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
                background: {cls.moon};
                border: 1px solid rgba(255, 255, 255, 0.78);
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: transparent;
                margin: 8px 0;
            }}
            QScrollBar::handle:vertical {{
                min-height: 42px;
                border-radius: 4px;
                background: rgba(201, 217, 226, 0.16);
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(217, 120, 85, 0.42);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """
