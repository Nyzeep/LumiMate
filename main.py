from __future__ import annotations

import sys


def main() -> int:
    try:
        from PyQt6.QtWidgets import QApplication
    except ModuleNotFoundError as exc:
        if exc.name != "PyQt6":
            raise
        print(
            "无法启动 LumiMate：当前 Python 环境未安装 PyQt6。\n"
            f"当前解释器：{sys.executable}\n"
            "请使用已安装 PyQt6 的项目解释器，或执行：python -m pip install PyQt6"
        )
        return 1

    from ui.layouts import LumiMainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("LumiMate")
    app.setOrganizationName("LumiMate")

    window = LumiMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
