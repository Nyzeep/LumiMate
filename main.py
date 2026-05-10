from __future__ import annotations

import sys
from pathlib import Path


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

    check_only = "--check" in sys.argv
    app_args = [arg for arg in sys.argv if arg != "--check"]

    try:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
    except ModuleNotFoundError as exc:
        if exc.name != "PySide6":
            raise
        print(
            "Unable to start LumiMate: PySide6 with QtQuick/QML support is not installed.\n"
            f"Current interpreter: {sys.executable}\n"
            f"Preferred interpreter: {_preferred_python()}\n"
            "Run: python -m pip install -r requirements.txt"
        )
        return 1

    from controllers import MainController
    from ui.bridge import AppBridge, ChatBridge, CompanionBridge, EmotionBridge, ModelBridge

    app = QGuiApplication(app_args)
    app.setApplicationName("LumiMate")
    app.setOrganizationName("LumiMate")

    controller = MainController()
    app_bridge = AppBridge(controller)
    model_bridge = ModelBridge(controller)
    chat_bridge = ChatBridge(controller)
    emotion_bridge = EmotionBridge(controller)
    companion_bridge = CompanionBridge()

    app.aboutToQuit.connect(controller.shutdown)

    engine = QQmlApplicationEngine()
    qml_root = project_root / "ui" / "qml"
    engine.addImportPath(str(qml_root))
    context = engine.rootContext()
    context.setContextProperty("appBridge", app_bridge)
    context.setContextProperty("modelBridge", model_bridge)
    context.setContextProperty("chatBridge", chat_bridge)
    context.setContextProperty("emotionBridge", emotion_bridge)
    context.setContextProperty("companionBridge", companion_bridge)

    main_qml = qml_root / "main.qml"
    engine.load(QUrl.fromLocalFile(str(main_qml)))
    if not engine.rootObjects():
        print(f"Unable to load QML root: {main_qml}")
        return 1

    if check_only:
        print(f"LumiMate QML startup check passed: {sys.executable}")
        return 0

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
