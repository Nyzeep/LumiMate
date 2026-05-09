from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QMessageBox, QVBoxLayout, QWidget, QMainWindow

from controllers import MainController
from ui.components import FloatingSidebar, TitleBar
from ui.effects import DreamscapeBackground
from ui.pages import ChatPage, CompanionPage, HomePage, SettingsPage, WorkbenchPage
from ui.themes import Theme
from ui.widgets import AnimatedStackWidget


class LumiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = MainController()
        self.setWindowTitle("LumiMate")
        self._apply_safe_start_size()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(Theme.app_qss())

        self.shell = QWidget()
        self.shell.setObjectName("windowShell")
        self.shell.setStyleSheet(
            """
            QWidget#windowShell {
                background-color: rgba(3, 8, 20, 0.82);
                border: 1px solid rgba(180,204,228,0.18);
                border-radius: 22px;
            }
            """
        )
        self.setCentralWidget(self.shell)
        self.background = DreamscapeBackground(self.shell)
        self.background.lower()
        self.pages: dict[str, QWidget] = {}
        self._build_ui()
        self._connect_signals()
        self._select_page("home")

    def _apply_safe_start_size(self) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            self.setMinimumSize(900, 560)
            self.resize(1280, 760)
            return
        available = screen.availableGeometry()
        safe_width = max(1, int(available.width() * 0.90))
        safe_height = max(1, int(available.height() * 0.90))
        min_width = min(920, max(560, int(available.width() * 0.62)), safe_width)
        min_height = min(600, max(440, int(available.height() * 0.62)), safe_height)
        width = min(max(min_width, int(available.width() * 0.88)), 1420, safe_width)
        height = min(max(min_height, int(available.height() * 0.86)), 860, safe_height)
        self.setMinimumSize(min_width, min_height)
        self.resize(width, height)
        self.move(
            available.x() + (available.width() - self.width()) // 2,
            available.y() + (available.height() - self.height()) // 2,
        )

    def _build_ui(self) -> None:
        root = QVBoxLayout(self.shell)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.title_bar = TitleBar()
        self.title_bar.minimize_requested.connect(self.showMinimized)
        self.title_bar.maximize_requested.connect(self._toggle_maximize)
        self.title_bar.close_requested.connect(self.close)
        root.addWidget(self.title_bar)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        self.sidebar = FloatingSidebar()
        content.addWidget(self.sidebar)

        self.stack = AnimatedStackWidget()
        self.stack.setObjectName("contentStack")
        self.stack.setStyleSheet("QStackedWidget#contentStack { background: transparent; }")
        self.home_page = HomePage()
        self.chat_page = ChatPage()
        self.companion_page = CompanionPage()
        self.workbench_page = WorkbenchPage()
        self.settings_page = SettingsPage()
        self.pages = {
            "home": self.home_page,
            "chat": self.chat_page,
            "companion": self.companion_page,
            "workbench": self.workbench_page,
            "settings": self.settings_page,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)
        content.addWidget(self.stack, 1)
        root.addLayout(content, 1)

    def _connect_signals(self) -> None:
        self.sidebar.page_requested.connect(self._select_page)
        self.home_page.open_chat_requested.connect(lambda: self._select_page("chat"))
        self.home_page.open_companion_requested.connect(lambda: self._select_page("companion"))
        self.home_page.open_workbench_requested.connect(lambda: self._select_page("workbench"))

        self.chat_page.start_requested.connect(self._start_conversation)
        self.chat_page.stop_requested.connect(self._stop_conversation)

        self.workbench_page.asr_browse.clicked.connect(lambda: self._browse(self.workbench_page.asr_edit, directory=True))
        self.workbench_page.llm_browse.clicked.connect(lambda: self._browse(self.workbench_page.llm_edit, directory=True))
        self.workbench_page.tts_browse.clicked.connect(lambda: self._browse(self.workbench_page.tts_edit, directory=True))
        self.workbench_page.audio_browse.clicked.connect(lambda: self._browse(self.workbench_page.audio_edit, directory=False))
        self.workbench_page.load_button.clicked.connect(self._load_models)
        self.workbench_page.stop_button.clicked.connect(self._stop_conversation)

        self.controller.log.connect(self.workbench_page.append_log)
        self.controller.progress.connect(self.workbench_page.set_progress)
        self.controller.state_changed.connect(self._on_state_changed)
        self.controller.loaded.connect(self._on_loaded)
        self.controller.user_text.connect(lambda text: self.chat_page.add_message(text, True))
        self.controller.assistant_text.connect(lambda text: self.chat_page.add_message(text, False))

    def _select_page(self, key: str) -> None:
        if key not in self.pages:
            return
        self.stack.setCurrentWidget(self.pages[key])
        self.sidebar.select(key)

    def _browse(self, edit, directory: bool) -> None:
        if directory:
            path = QFileDialog.getExistingDirectory(self, "选择目录")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if path:
            edit.setText(path)

    def _load_models(self) -> None:
        try:
            config = self.workbench_page.config()
        except ValueError:
            QMessageBox.warning(self, "参数错误", "最大 Token 必须是数字。")
            return
        started = self.controller.load_models(config)
        if not started:
            self.workbench_page.append_log("模型正在处理其他任务，请稍后再试。")

    def _start_conversation(self) -> None:
        if self.controller.start_conversation():
            self.chat_page.set_running(True)
            self.workbench_page.append_log("Lumi 正在聆听。")

    def _stop_conversation(self) -> None:
        self.controller.stop_conversation()
        self.chat_page.set_running(False)
        self.workbench_page.append_log("对话已停下。")

    def _on_state_changed(self, state: str, message: str) -> None:
        self.workbench_page.set_model_state(state, message)
        self.chat_page.set_ready(state in {"ready", "running"})
        self.chat_page.set_running(state == "running")

    def _on_loaded(self, success: bool) -> None:
        self.workbench_page.set_loaded(success)
        self.chat_page.set_ready(success)

    def _toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def resizeEvent(self, event) -> None:
        self.background.setGeometry(self.shell.rect())
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect().adjusted(1, 1, -1, -1)), 24, 24)
        painter.fillPath(path, QColor(0, 0, 0, 1))
        super().paintEvent(event)

    def closeEvent(self, event) -> None:
        self.controller.shutdown()
        QApplication.instance().quit()
        super().closeEvent(event)
