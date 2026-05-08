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
    sm: int = 16
    md: int = 24
    lg: int = 32
    xl: int = 40


@dataclass(frozen=True)
class Motion:
    hover: int = 360
    page: int = 520
    breath: int = 4200
    ambient_tick: int = 110


class Theme:
    ink = "#0E2437"
    ink_deep = "#071827"
    twilight = "#17324A"
    mist = "#D7E3EC"
    moon = "#F0E6D8"
    moon_soft = "#E8D7CA"
    dusty_purple = "#AFA3C8"
    mist_blue = "#7FA6BC"
    pale_cyan = "#B9DCE4"
    flower = "#C995A6"
    text = "#EEF3F5"
    text_dark = "#213646"
    muted = "#AEBCC6"
    dim = "#728291"
    line = "rgba(238, 243, 245, 0.16)"
    line_soft = "rgba(238, 243, 245, 0.09)"
    panel = "rgba(232, 239, 243, 0.105)"
    panel_warm = "rgba(248, 235, 224, 0.68)"
    panel_dark = "rgba(12, 31, 48, 0.56)"
    shadow = QColor(3, 11, 18, 70)

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
                background-color: rgba(10, 25, 39, 0.94);
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 12px;
                padding: 7px 10px;
            }}
            QProgressBar {{
                min-height: 7px;
                max-height: 7px;
                border: 0;
                border-radius: 3px;
                background: rgba(255, 255, 255, 0.12);
                color: transparent;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.mist_blue}, stop:0.55 {cls.dusty_purple}, stop:1 {cls.pale_cyan});
            }}
            QSlider::groove:horizontal {{
                height: 5px;
                border-radius: 2px;
                background: rgba(255, 255, 255, 0.12);
            }}
            QSlider::sub-page:horizontal {{
                border-radius: 2px;
                background: rgba(185, 220, 228, 0.72);
            }}
            QSlider::handle:horizontal {{
                width: 15px;
                height: 15px;
                margin: -5px 0;
                border-radius: 7px;
                background: {cls.moon};
                border: 1px solid rgba(255, 255, 255, 0.64);
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: transparent;
                margin: 8px 0;
            }}
            QScrollBar::handle:vertical {{
                min-height: 42px;
                border-radius: 4px;
                background: rgba(238, 243, 245, 0.16);
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(238, 243, 245, 0.26);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """
