from __future__ import annotations

import os
import sys
from pathlib import Path


CHECK_FLAG = "--check"
WINDOWED_FLAG = "--windowed"
DEV_URL_ENV = "LUMIMATE_WEB_DEV_URL"


def _preferred_python() -> Path:
    project_root = Path(__file__).resolve().parent
    from core.bootstrap import AppBootstrap

    return AppBootstrap.preferred_python(project_root)


def main() -> int:
    project_root = Path(__file__).resolve().parent
    from core.bootstrap import AppBootstrap

    bootstrap = AppBootstrap.ensure_environment(project_root)
    if not bootstrap.ok:
        print(bootstrap.message)
        return 1

    check_only = CHECK_FLAG in sys.argv
    windowed = WINDOWED_FLAG in sys.argv or os.environ.get("LUMIMATE_WINDOWED") == "1"
    app_args = [arg for arg in sys.argv if arg not in {CHECK_FLAG, WINDOWED_FLAG}]

    try:
        from PySide6.QtCore import Qt, QUrl
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QApplication, QMainWindow

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
    from ui.bridge import AppBridge, ChatBridge, CompanionBridge, EmotionBridge, ModelBridge, WindowBridge

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
    window_bridge = WindowBridge(window)

    app.aboutToQuit.connect(controller.shutdown)

    view = QWebEngineView(window)
    view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    view.setStyleSheet("background: transparent; border: 0;")

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
    channel.registerObject("windowBridge", window_bridge)
    page.setWebChannel(channel)

    view.setPage(page)
    window.setCentralWidget(view)
    view.setUrl(frontend_url)

    if windowed:
        window.resize(1600, 900)
        window.show()
    else:
        window.showFullScreen()

    if not frontend_url.isValid():
        print(f"Unable to load Web frontend: {frontend_url.toString()}")
        return 1

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
