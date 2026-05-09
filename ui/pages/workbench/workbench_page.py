from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import AssistantConfig
from ui.components import CompanionScene, FloatingInput, GlassButton, GlowButton, ModernScrollArea, PageContainer, PoeticPanel, SceneCard
from ui.themes import Theme


class WorkbenchPage(PageContainer):
    def __init__(self, parent=None):
        super().__init__(parent, margins=(0, 0, 0, 0), spacing=0)
        self._build_ui()
        self.set_config(AssistantConfig.defaults())
        self.connect_internal_signals()

    def _build_ui(self) -> None:
        self.scroll_area = ModernScrollArea()
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setContentsMargins(44, 34, 42, 34)
        content_layout.setSpacing(18)
        self.scroll_area.setWidget(self.scroll_content)
        self.root.addWidget(self.scroll_area)
        self.root = content_layout

        title = QLabel("工作台")
        title.setFont(QFont("Microsoft YaHei UI", 30, QFont.Weight.DemiBold))
        subtitle = QLabel("整理 Lumi 的核心能力，复杂参数默认安静地收起来。")
        subtitle.setStyleSheet("color: rgba(238,243,245,0.62);")
        self.root.addWidget(title)
        self.root.addWidget(subtitle)

        top = QHBoxLayout()
        top.setSpacing(16)
        self.model_state_card = SceneCard("模型状态", "未加载", "等待启动。", warm=True)
        self.voice_state_card = SceneCard("语音状态", "待机", "开始对话后进入聆听。", warm=True)
        self.plugin_state_card = SceneCard("扩展", "预留", "角色资源、记忆同步与外部工具。", warm=True)
        top.addWidget(self.model_state_card)
        top.addWidget(self.voice_state_card)
        top.addWidget(self.plugin_state_card)
        self.root.addLayout(top)

        workbench_stage = PoeticPanel(radius=26)
        workbench_stage_layout = QVBoxLayout(workbench_stage)
        workbench_stage_layout.setContentsMargins(0, 0, 0, 0)
        workbench_scene = CompanionScene("workbench")
        workbench_scene.setFixedHeight(150)
        workbench_stage_layout.addWidget(workbench_scene)
        self.root.addWidget(workbench_stage)

        self.progress_label = QLabel("待机")
        self.progress_label.setStyleSheet("color: rgba(238,243,245,0.68);")
        self.progress_bar = QProgressBar()
        self.root.addWidget(self.progress_label)
        self.root.addWidget(self.progress_bar)

        actions = QHBoxLayout()
        actions.setSpacing(12)
        self.load_button = GlowButton("加载全部模型")
        self.stop_button = GlassButton("停止语音")
        self.advanced_button = QPushButton("高级设置  ▾")
        self.advanced_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.advanced_button.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 0; color: {Theme.text}; font-weight: 700; text-align: left; }}"
        )
        actions.addWidget(self.load_button)
        actions.addWidget(self.stop_button)
        actions.addWidget(self.advanced_button)
        actions.addStretch()
        self.root.addLayout(actions)

        self.advanced_panel = PoeticPanel(radius=30)
        self.advanced_panel.setMinimumHeight(410)
        self.advanced_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        advanced_layout = QVBoxLayout(self.advanced_panel)
        advanced_layout.setContentsMargins(20, 20, 20, 20)
        advanced_layout.setSpacing(18)
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnMinimumWidth(0, 88)
        grid.setColumnMinimumWidth(2, 82)
        grid.setColumnStretch(1, 1)
        for row in range(6):
            grid.setRowMinimumHeight(row, 42)

        self.asr_edit = FloatingInput()
        self.llm_edit = FloatingInput()
        self.tts_edit = FloatingInput()
        self.audio_edit = FloatingInput()
        self.ref_text_edit = FloatingInput()
        self.role_edit = FloatingInput()
        self.asr_browse = GlassButton("选择")
        self.llm_browse = GlassButton("选择")
        self.tts_browse = GlassButton("选择")
        self.audio_browse = GlassButton("选择")

        self._add_field(grid, 0, "ASR 模型", self.asr_edit, self.asr_browse)
        self._add_field(grid, 1, "LLM 模型", self.llm_edit, self.llm_browse)
        self._add_field(grid, 2, "TTS 目录", self.tts_edit, self.tts_browse)
        self._add_field(grid, 3, "参考音频", self.audio_edit, self.audio_browse)
        self._add_field(grid, 4, "参考文本", self.ref_text_edit)
        self._add_field(grid, 5, "角色名", self.role_edit)
        advanced_layout.addLayout(grid)

        controls = QGridLayout()
        controls.setHorizontalSpacing(16)
        controls.setVerticalSpacing(12)
        controls.setColumnMinimumWidth(0, 88)
        controls.setColumnMinimumWidth(2, 64)
        controls.setColumnStretch(1, 1)
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setRange(1, 10)
        self.duration_label = QLabel("3 秒")
        self.energy_slider = QSlider(Qt.Orientation.Horizontal)
        self.energy_slider.setRange(1, 20)
        self.energy_label = QLabel("0.005")
        self.token_edit = FloatingInput()
        self.token_edit.setFixedWidth(120)
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.energy_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        controls.addWidget(QLabel("录音片段"), 0, 0)
        controls.addWidget(self.duration_slider, 0, 1)
        controls.addWidget(self.duration_label, 0, 2)
        controls.addWidget(QLabel("能量阈值"), 1, 0)
        controls.addWidget(self.energy_slider, 1, 1)
        controls.addWidget(self.energy_label, 1, 2)
        controls.addWidget(QLabel("最大 Token"), 2, 0)
        controls.addWidget(self.token_edit, 2, 1, 1, 2)
        advanced_layout.addLayout(controls)
        self.advanced_panel.setVisible(False)
        self.root.addWidget(self.advanced_panel)

        log_panel = PoeticPanel(radius=30)
        log_layout = QVBoxLayout(log_panel)
        log_layout.setContentsMargins(18, 16, 18, 16)
        log_layout.setSpacing(10)
        log_title = QLabel("运行记录")
        log_title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.DemiBold))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        self.log_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: rgba(3, 8, 20, 0.48);
                border: 1px solid rgba(180,204,228,0.14);
                border-radius: 18px;
                padding: 12px;
                color: {Theme.text};
                font-family: Consolas, "Microsoft YaHei UI";
            }}
            """
        )
        self.clear_log_button = GlassButton("清空记录")
        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log_text)
        log_layout.addWidget(self.clear_log_button)
        self.root.addWidget(log_panel, 1)

    def _add_field(self, grid: QGridLayout, row: int, label_text: str, edit: FloatingInput, button: GlassButton | None = None) -> None:
        label = QLabel(label_text)
        label.setStyleSheet("color: rgba(238,243,245,0.66); font-weight: 650;")
        label.setMinimumWidth(88)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        edit.setMinimumWidth(280)
        edit.setFixedHeight(40)
        grid.addWidget(label, row, 0)
        if button:
            grid.addWidget(edit, row, 1)
            button.setFixedSize(74, 40)
            grid.addWidget(button, row, 2)
        else:
            grid.addWidget(edit, row, 1, 1, 2)

    def connect_internal_signals(self) -> None:
        self.duration_slider.valueChanged.connect(lambda value: self.duration_label.setText(f"{value} 秒"))
        self.energy_slider.valueChanged.connect(lambda value: self.energy_label.setText(f"{value / 1000:.3f}"))
        self.clear_log_button.clicked.connect(self.log_text.clear)
        self.advanced_button.clicked.connect(self._toggle_advanced)

    def _toggle_advanced(self) -> None:
        visible = not self.advanced_panel.isVisible()
        self.advanced_panel.setVisible(visible)
        self.advanced_button.setText("高级设置  ▴" if visible else "高级设置  ▾")

    def set_config(self, config: AssistantConfig) -> None:
        self.asr_edit.setText(config.asr_path)
        self.llm_edit.setText(config.llm_path)
        self.tts_edit.setText(config.tts_model_dir)
        self.audio_edit.setText(config.ref_audio_path)
        self.ref_text_edit.setText(config.ref_text)
        self.role_edit.setText(config.tts_character)
        self.duration_slider.setValue(config.chunk_sec)
        self.energy_slider.setValue(max(1, min(20, int(config.energy_threshold * 1000))))
        self.token_edit.setText(str(config.max_new_tokens))

    def config(self) -> AssistantConfig:
        return AssistantConfig(
            asr_path=self.asr_edit.text().strip(),
            llm_path=self.llm_edit.text().strip(),
            tts_model_dir=self.tts_edit.text().strip(),
            ref_audio_path=self.audio_edit.text().strip(),
            ref_text=self.ref_text_edit.text().strip(),
            tts_character=self.role_edit.text().strip() or "菲比",
            chunk_sec=self.duration_slider.value(),
            energy_threshold=self.energy_slider.value() / 1000.0,
            max_new_tokens=max(16, int(self.token_edit.text() or "100")),
        )

    def append_log(self, message: str) -> None:
        self.log_text.append(message)

    def set_progress(self, step: int, total: int, message: str) -> None:
        self.progress_bar.setMaximum(max(total, 1))
        self.progress_bar.setValue(step)
        self.progress_label.setText(message)

    def set_model_state(self, state: str, message: str) -> None:
        state_names = {
            "idle": "未加载",
            "validating": "校验中",
            "loading_asr": "加载 ASR",
            "loading_llm": "加载 LLM",
            "loading_tts": "初始化 TTS",
            "ready": "已就绪",
            "running": "聆听中",
            "stopping": "停止中",
            "failed": "加载失败",
        }
        self.model_state_card.set_value(state_names.get(state, state), message)
        if state == "running":
            self.voice_state_card.set_value("聆听中", "正在接收你的声音。")
        elif state in {"ready", "failed", "idle"}:
            self.voice_state_card.set_value("待机", "开始对话后进入聆听。")
        self.load_button.setEnabled(state not in {"validating", "loading_asr", "loading_llm", "loading_tts", "stopping"})

    def set_loaded(self, success: bool) -> None:
        self.load_button.setEnabled(True)
        if success:
            self.load_button.setText("模型已就绪")
            self.append_log("模型加载完成，可以开始对话。")
        else:
            self.load_button.setText("加载全部模型")
            self.append_log("模型加载失败，请查看运行记录。")
