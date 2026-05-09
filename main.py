from __future__ import annotations

import sys
from pathlib import Path


def _preferred_python() -> Path:
    project_root = Path(__file__).resolve().parent
    return project_root.parent / ".venv" / "Scripts" / "python.exe"


def _relaunch_with_project_venv() -> None:
    project_root = Path(__file__).resolve().parent
    preferred_python = _preferred_python()
    if not preferred_python.exists():
        return

    current_python = Path(sys.executable).resolve()
    if current_python == preferred_python.resolve():
        return

    import os

    os.execv(str(preferred_python), [str(preferred_python), str(project_root / "main.py"), *sys.argv[1:]])


def main() -> int:
    _relaunch_with_project_venv()
    check_only = "--check" in sys.argv
    app_args = [arg for arg in sys.argv if arg != "--check"]

    try:
        from PyQt6.QtWidgets import QApplication
    except ModuleNotFoundError as exc:
        if exc.name != "PyQt6":
            raise
        print(
            "无法启动 LumiMate：当前 Python 环境未安装 PyQt6。\n"
            f"当前解释器：{sys.executable}\n"
            f"推荐解释器：{_preferred_python()}\n"
            "请先在项目目录执行：python -m pip install -r requirements.txt\n"
            "或切换到已经安装项目依赖的 Python 解释器。"
        )
        return 1

    from ui.layouts import LumiMainWindow

    app = QApplication(app_args)
    app.setApplicationName("LumiMate")
    app.setOrganizationName("LumiMate")

    window = LumiMainWindow()
    if check_only:
        print(f"LumiMate startup check passed: {sys.executable}")
        window.close()
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
