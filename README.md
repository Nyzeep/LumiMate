# LumiMate

LumiMate 是一个以“空间情绪系统”为核心的桌面 AI 陪伴应用。当前运行时采用 `Python + PySide6 + QWebEngineView + Vue 3`：Python 负责窗口、桥接和底层逻辑，Web 前端负责完整视觉渲染。

LumiMate is a desktop AI companion built around a spatial emotional system. The current runtime uses `Python + PySide6 + QWebEngineView + Vue 3`: Python owns the window, bridge, and backend logic, while the web layer owns the full visual interface.

## 运行 / Run

创建虚拟环境并安装 Python 依赖：

Create a virtual environment and install Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

构建 WebEngine 前端：

Build the WebEngine frontend:

```powershell
cd ui\web
npm install
npm run build
cd ..\..
```

启动应用：

Launch the app:

```bat
run_lumi.bat
```

也可以直接运行：

Or run directly:

```powershell
python main.py
```

默认启动为全屏；开发调试时可以使用窗口模式：

The default launch is fullscreen. Use windowed mode for development:

```powershell
python main.py --windowed
```

## 目录结构 / Structure

```text
config/       运行配置、默认值和用户设置 / Runtime config, defaults, and user settings
controllers/  UI 与服务层控制流 / UI-to-service controller flow
core/         启动、完整性检查、国际化和语音核心 / Bootstrap, integrity, i18n, and voice assistant core
services/     模型加载、运行时服务和更新器 / Model loading, runtime service, and updater
ui/bridge/    暴露给 QWebChannel 的 PySide6 桥接对象 / PySide6 bridge objects exposed to QWebChannel
ui/web/       Vue 3 WebEngine 前端 / Vue 3 WebEngine frontend
ui/qml/       暂时保留的旧 QML 回退界面 / Legacy QML runtime kept temporarily as a fallback
resources/    参考音频与视觉资源 / Reference audio and visual assets
tools/        本地维护脚本 / Local maintenance scripts
背景图片/      项目现有背景资源 / Existing project background assets
```

## UI 架构 / UI Runtime

空间界面主要由以下部分组成：

The spatial UI is centered on:

- `main.py`：透明、无边框的 WebEngine 容器 / transparent frameless WebEngine container
- `ui/bridge/`：前端通过 QWebChannel 调用的桥接对象 / QWebChannel objects used by the frontend
- `ui/web/src/`：Vue 首页空间、全局视觉系统和 SVG 几何界面 / Vue home space, global visual system, and SVG geometric interface
- `背景图片/`：现有项目背景图，前端通过 `appBridge` 获取 / existing backgrounds selected through `appBridge`

混合架构会把背景资源映射、模型加载、文件访问等底层能力留在 Python 侧；WebEngine 前端只负责沉浸式玻璃拟态 UI、页面状态和交互表达。

The hybrid architecture keeps background mappings, model loading, and file access in Python. The WebEngine frontend focuses on the immersive glassmorphism UI, scene state, and interaction layer.

## 运行依赖 / Runtime Dependencies

模型加载仍依赖本地 ASR / TTS 包和本地模型资源。完整语音交互需要确认以下资源存在：

Model loading still depends on local ASR / TTS packages and local model assets. For full voice interaction, make sure these resources are present:

- `models/`
- `GenieData/`
- any required precompiled `flash_attn` resources

这些大型运行时资源不会默认提交到仓库。

These large runtime assets are not committed to the repository by default.
