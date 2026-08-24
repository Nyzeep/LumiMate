<p align="center">
  <img src="./resources/ui/author_avatar.jpg" width="88" alt="Nyzeep avatar" />
</p>

<h1 align="center">LumiMate</h1>

<p align="center">
  一个安静、深邃、会呼吸的桌面 AI 陪伴空间。<br />
  A quiet, cosmic desktop AI companion space with ritual, breath, and presence.
</p>

<p align="center">
  <a href="https://github.com/Nyzeep/LumiMate"><img alt="Repository" src="https://img.shields.io/badge/GitHub-Nyzeep%2FLumiMate-07111f?style=flat-square&logo=github&logoColor=f7c873"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-Runtime-07111f?style=flat-square&logo=python&logoColor=f7c873">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Service-07111f?style=flat-square&logo=fastapi&logoColor=f7c873">
  <img alt="Tauri" src="https://img.shields.io/badge/Tauri-v2-07111f?style=flat-square&logo=tauri&logoColor=f7c873">
  <img alt="Vue" src="https://img.shields.io/badge/Vue_3-UI-07111f?style=flat-square&logo=vuedotjs&logoColor=f7c873">
  <img alt="Vite" src="https://img.shields.io/badge/Vite-Build-07111f?style=flat-square&logo=vite&logoColor=f7c873">
</p>

## 中文说明

LumiMate 不是传统聊天窗口，而是一个围绕 Lumi 构建的数字意识空间。它把本地模型、语音链路、聊天输入、陪伴舞台、设置与运行状态组织成九个沉浸式空间，让用户进入的是一个安静的 AI companion 场域，而不是一组冰冷的工具面板。

当前版本已从 `PySide6 + Qt WebEngine + QWebChannel` 迁移为 `Tauri v2 + Vue 3 + Vite + Python FastAPI Runtime`。这样做的核心原因是：系统 WebView2 在 Windows 上的帧同步、窗口行为和 GPU 合成稳定性更适合 LumiMate 这种高质感动效 UI；Python 继续负责模型、语音、下载和本地运行时服务。

### 功能亮点

- 九空间结构：首页、对话、陪伴、工作台、加载、存储、设置、个性化、关于。
- 深蓝金色宇宙风 UI，保留现有按钮、星环、泛光、背景与微动效系统。
- Python FastAPI Runtime 提供 HTTP 命令接口与 WebSocket 状态推送。
- Tauri 原生窗口提供可缩放、可最小化、可最大化、可关闭的桌面体验。
- 工作台支持扫描本地 `models/`、选择模型、触发加载和模型下载入口。
- 对话空间支持文本输入、语音启动、运行状态和消息流反馈。
- 背景资源固定来自项目根目录的 `背景图片/背景1.png` 到 `背景4.png`。

### 架构

```text
LumiMate
├─ Tauri v2 desktop shell
│  └─ system WebView2 / native window
├─ Vue 3 + Vite UI
│  ├─ nine-space scene system
│  ├─ runtime ambient motion
│  └─ HTTP + WebSocket runtime client
└─ Python FastAPI Runtime
   ├─ MainController
   ├─ model / download / assistant services
   └─ local ASR / LLM / TTS pipeline
```

### 开发环境

你需要准备：

- Python 3.11 或更新版本
- Node.js 22.19 或更新版本
- Rust 工具链与 Cargo
- Windows 上推荐安装 WebView2 Runtime

首次安装前端依赖：

```powershell
cd ui\web
npm install
```

检查 Python Runtime：

```powershell
python launcher.py --api --check
python launcher.py --check
```

启动 Tauri 开发环境：

```powershell
cd ui\web
npm run tauri:dev
```

### Task Agent 任务舱

任务舱位于“运行空间 → 工作台 → 任务舱”。Tauri 启动 Runtime 时会启用 Task Agent，并通过 DeepSeek Harness 的 Node 载体执行任务。

使用前请在项目根目录的 `.env` 配置有效的 `DEEPSEEK_API_KEY`；该文件不应提交到仓库。Windows 开发环境还需要 Node.js 22.19 或更新版本，任务发起后应先显示“规划中”或“等待计划确认”。

> 提示：`harnessAvailable: true` 只表示 Harness 已装配；若任务显示认证失败，请更新 `DEEPSEEK_API_KEY`，不要把按钮点击成功视为任务已完成。

构建前端：

```powershell
cd ui\web
npm run build
```

构建桌面应用：

```powershell
cd ui\web
npm run tauri:build
```

单独启动 Python Runtime：

```powershell
python launcher.py --api --host 127.0.0.1 --port 8765
```

前端也可以通过 URL 参数连接指定 Runtime：

```text
http://127.0.0.1:5173/?apiBase=http://127.0.0.1:8765
```

> 提示：Runtime 默认只允许本地开发与 Tauri 页面来源跨域访问；如需允许其他来源，请设置环境变量 `LUMIMATE_CORS_ORIGINS`（逗号分隔的来源白名单）。

### 模型目录

LumiMate 默认扫描：

```text
models/
├─ asr_model/
├─ llm_model/
└─ tts_model/
```

如果缺少 ASR 或 LLM，进入工作台后可以使用模型星系入口下载或导入。本地模型文件通常较大，`models/` 不建议提交到仓库。

### 目录结构

```text
LumiMate/
├─ launcher.py              Python Runtime 启动器
├─ main.py                  兼容入口，转发到 launcher.py
├─ runtime/                 FastAPI Runtime 与 WebSocket 服务
├─ controllers/             主控制器
├─ services/                模型、下载、更新与助手服务
├─ core/                    启动、完整性、事件和语音核心逻辑
├─ config/                  应用配置与用户设置模板
├─ ui/
│  ├─ web/                  Vue 3 + Vite 前端与 Tauri 工程
│  └─ assets/               资源清单
├─ resources/               作者头像、参考音频、界面纹理
└─ 背景图片/                LumiMate 正式背景源
```

> 用户个人设置保存在 config/user_settings.json（本地状态，不纳入版本控制），新环境可参考 config/user_settings.example.json 创建。

### 发布注意事项

- GitHub release 压缩包不应包含 `.venv/`、`node_modules/`、`models/`、`GenieData/`、缓存目录或 skill/agent 本地文件。
- 如果要发布可执行安装包，请先完成 `npm run tauri:build`，并确认 Python Runtime 的打包策略已经覆盖目标机器。
- 当前源码模式下，Tauri 会通过本机 Python 或项目 `.venv` 启动 Runtime。

## English

LumiMate is a desktop AI companion space. It is designed to feel less like a utility window and more like entering a quiet digital room where Lumi can listen, respond, and wake local model nodes with a sense of presence.

The project now uses `Tauri v2 + Vue 3 + Vite + Python FastAPI Runtime`. The UI runs in the system WebView, while Python remains responsible for local models, voice services, downloads, and runtime orchestration.

### Highlights

- Nine immersive spaces: Home, Chat, Companion, Workbench, Loading, Storage, Settings, Personality, and About.
- Existing deep blue and gold cosmic visual language, buttons, glow, orbit motion, and background assets are preserved.
- FastAPI exposes HTTP commands and WebSocket state updates.
- Tauri provides a native, resizable, stable desktop window.
- The Workbench scans local models, selects nodes, starts loading, and provides download entry points.
- The background set is sourced from `背景图片/背景1.png` through `背景图片/背景4.png`.

### Development

```powershell
cd ui\web
npm install
npm run tauri:dev
```

Runtime checks:

```powershell
python launcher.py --api --check
python launcher.py --check
```

Frontend build:

```powershell
cd ui\web
npm run build
```

Desktop build:

```powershell
cd ui\web
npm run tauri:build
```

### Repository

- Author: `Nyzeep`
- Repository: <https://github.com/Nyzeep/LumiMate>
- Product direction: a spatial AI companion system with emotion, ritual, and breath.
