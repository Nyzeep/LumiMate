from __future__ import annotations

import os
import sys
from pathlib import Path


CHECK_FLAG = "--check"
WINDOWED_FLAG = "--windowed"
DEV_URL_ENV = "LUMIMATE_WEB_DEV_URL"


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _preferred_python() -> Path:
    project_root = _project_root()
    from core.bootstrap import AppBootstrap

    return AppBootstrap.preferred_python(project_root)


def main() -> int:
    project_root = _project_root()
    from core.bootstrap import AppBootstrap

    bootstrap = AppBootstrap.ensure_environment(project_root)
    if not bootstrap.ok:
        print(bootstrap.message)
        return 1

    check_only = CHECK_FLAG in sys.argv
    windowed = WINDOWED_FLAG in sys.argv or os.environ.get("LUMIMATE_WINDOWED") == "1"
    app_args = [arg for arg in sys.argv if arg not in {CHECK_FLAG, WINDOWED_FLAG}]

    try:
        from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, QTimer, QUrl
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import (
            QApplication,
            QFrame,
            QGraphicsOpacityEffect,
            QLabel,
            QMainWindow,
            QVBoxLayout,
            QWidget,
        )

        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

        from PySide6.QtWebChannel import QWebChannel
        from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
        from PySide6.QtWebEngineWidgets import QWebEngineView
    except ModuleNotFoundError as exc:
        if not str(exc.name).startswith("PySide6"):
            raise
        print(
            "Unable to start LumiMate: PySide6 with QtWebEngine support is not installed.\n"
            f"Current interpreter: {sys.executable}\n"
            f"Preferred interpreter: {_preferred_python()}\n"
            "Run: python -m pip install -r requirements.txt"
        )
        return 1

    frontend_entry = project_root / "ui" / "web" / "dist" / "index.html"
    if check_only:
        if not frontend_entry.exists():
            print(f"Unable to find built Web frontend: {frontend_entry}")
            print("Run: cd ui\\web && npm install && npm run build")
            return 1
        print(f"LumiMate WebEngine startup check passed: {sys.executable}")
        print(f"Frontend entry: {frontend_entry}")
        return 0

    from controllers import MainController
    from ui.bridge import AppBridge, ChatBridge, CompanionBridge, EmotionBridge, ModelBridge, ShellBridge, WindowBridge

    class BootOverlay(QFrame):
        def __init__(self, parent: QWidget):
            super().__init__(parent)
            self.setObjectName("bootOverlay")
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setStyleSheet(
                "#bootOverlay {"
                "background: rgba(6, 17, 37, 244);"
                "border: 1px solid rgba(255, 214, 180, 28);"
                "}"
                "QLabel#bootTitle {"
                "color: rgba(245, 234, 223, 240);"
                "font-size: 34px;"
                "font-weight: 300;"
                "}"
                "QLabel#bootSubtitle {"
                "color: rgba(233, 216, 205, 168);"
                "font-size: 12px;"
                "letter-spacing: 1px;"
                "text-transform: uppercase;"
                "}"
            )
            layout = QVBoxLayout(self)
            layout.setContentsMargins(48, 48, 48, 48)
            layout.addStretch(1)
            title = QLabel("LumiMate", self)
            title.setObjectName("bootTitle")
            subtitle = QLabel("Lumi 正在展开空间", self)
            subtitle.setObjectName("bootSubtitle")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            layout.addSpacing(12)
            layout.addWidget(subtitle)
            layout.addStretch(1)
            self._effect = QGraphicsOpacityEffect(self)
            self._effect.setOpacity(1.0)
            self.setGraphicsEffect(self._effect)
            self.setGeometry(parent.rect())
            parent.installEventFilter(self)

        @property
        def opacity_effect(self) -> QGraphicsOpacityEffect:
            return self._effect

        def eventFilter(self, watched, event):
            if watched is self.parent() and event.type() in {QEvent.Type.Resize, QEvent.Type.Move}:
                self.setGeometry(self.parent().rect())
            return super().eventFilter(watched, event)

    app = QApplication(app_args)
    app.setApplicationName("LumiMate")
    app.setOrganizationName("LumiMate")

    dev_url = os.environ.get(DEV_URL_ENV, "").strip()
    if dev_url:
        frontend_url = QUrl(dev_url)
    else:
        if not frontend_entry.exists():
            print(f"Unable to find built Web frontend: {frontend_entry}")
            print("Run: cd ui\\web && npm install && npm run build")
            return 1
        frontend_url = QUrl.fromLocalFile(str(frontend_entry))

    window = QMainWindow()
    window.setWindowTitle("LumiMate")
    window.setMinimumSize(1280, 720)
    window.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    window.setStyleSheet("background: transparent;")

    controller = MainController()
    app_bridge = AppBridge(controller)
    model_bridge = ModelBridge(controller)
    chat_bridge = ChatBridge(controller)
    emotion_bridge = EmotionBridge(controller)
    companion_bridge = CompanionBridge(controller)
    shell_bridge = ShellBridge()
    window_bridge = WindowBridge(window)

    app.aboutToQuit.connect(controller.shutdown)

    view = QWebEngineView(window)
    view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    view.setStyleSheet("background: transparent; border: 0;")
    view_effect = QGraphicsOpacityEffect(view)
    view_effect.setOpacity(1.0)
    view.setGraphicsEffect(view_effect)

    page = QWebEnginePage(view)
    page.setBackgroundColor(QColor(0, 0, 0, 0))
    settings = page.settings()
    settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    channel = QWebChannel(page)
    channel.registerObject("appBridge", app_bridge)
    channel.registerObject("modelBridge", model_bridge)
    channel.registerObject("chatBridge", chat_bridge)
    channel.registerObject("emotionBridge", emotion_bridge)
    channel.registerObject("companionBridge", companion_bridge)
    channel.registerObject("shellBridge", shell_bridge)
    channel.registerObject("windowBridge", window_bridge)
    page.setWebChannel(channel)

    view.setPage(page)
    window.setCentralWidget(view)
    overlay = BootOverlay(window)
    overlay.raise_()
    reveal_started = False
    handoff_failsafe = QTimer(window)
    handoff_failsafe.setSingleShot(True)
    absolute_failsafe = QTimer(window)
    absolute_failsafe.setSingleShot(True)

    overlay_animation = QPropertyAnimation(overlay.opacity_effect, b"opacity", window)
    overlay_animation.setDuration(420)
    overlay_animation.setStartValue(1.0)
    overlay_animation.setEndValue(0.0)
    overlay_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
    overlay_animation.finished.connect(overlay.hide)

    def reveal_frontend() -> None:
        nonlocal reveal_started
        if reveal_started:
            return
        if shell_bridge.bootPhase == "revealed":
            return
        reveal_started = True
        handoff_failsafe.stop()
        absolute_failsafe.stop()
        shell_bridge.set_phase("revealing")
        view_effect.setOpacity(1.0)
        overlay.raise_()
        overlay_animation.start()
        QTimer.singleShot(460, lambda: shell_bridge.set_phase("revealed"))

    def force_reveal_frontend() -> None:
        reveal_frontend()

    page.loadStarted.connect(lambda: shell_bridge.set_phase("page-loading"))

    def on_page_loaded(success: bool) -> None:
        if success:
            shell_bridge.set_phase("page-loaded")
            handoff_failsafe.start(6000)
        else:
            shell_bridge.set_phase("load-failed")

    page.loadFinished.connect(on_page_loaded)
    shell_bridge.frontendReadyRequested.connect(reveal_frontend)
    handoff_failsafe.timeout.connect(reveal_frontend)
    absolute_failsafe.timeout.connect(force_reveal_frontend)
    view.setUrl(frontend_url)

    if windowed:
        window.resize(1600, 900)
        window.show()
    else:
        window.showFullScreen()
    absolute_failsafe.start(3500)

    if not frontend_url.isValid():
        print(f"Unable to load Web frontend: {frontend_url.toString()}")
        return 1

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
