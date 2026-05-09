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
    ink = "#07111F"
    ink_deep = "#030814"
    twilight = "#0F1B2C"
    midnight = "#101B2C"
    panel_blue = "#142033"
    mist = "#DDE8F1"
    moon = "#F4E7D6"
    moon_soft = "#D9E9F6"
    accent = "#E2764F"
    accent_soft = "#F3A476"
    dusty_purple = "#AFA3C8"
    mist_blue = "#88AECB"
    pale_cyan = "#B7D8E8"
    flower = "#E2764F"
    text = "#F4F8FB"
    text_dark = "#F4F8FB"
    muted = "#AAB8C8"
    dim = "#77869A"
    line = "rgba(180, 204, 228, 0.18)"
    line_soft = "rgba(180, 204, 228, 0.10)"
    panel = "rgba(18, 29, 46, 0.76)"
    panel_warm = "rgba(21, 32, 49, 0.78)"
    panel_dark = "rgba(11, 20, 34, 0.78)"
    shadow = QColor(0, 0, 0, 130)

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
                background-color: rgba(10, 17, 29, 0.96);
                border: 1px solid rgba(226, 118, 79, 0.36);
                border-radius: 12px;
                padding: 7px 10px;
            }}
            QProgressBar {{
                min-height: 8px;
                max-height: 8px;
                border: 0;
                border-radius: 4px;
                background: rgba(180, 204, 228, 0.13);
                color: transparent;
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.accent}, stop:0.62 {cls.accent_soft}, stop:1 {cls.pale_cyan});
            }}
            QSlider::groove:horizontal {{
                height: 5px;
                border-radius: 2px;
                background: rgba(180, 204, 228, 0.16);
            }}
            QSlider::sub-page:horizontal {{
                border-radius: 2px;
                background: rgba(226, 118, 79, 0.86);
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
                background: rgba(180, 204, 228, 0.18);
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(226, 118, 79, 0.48);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """
