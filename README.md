<p align="center">
  <img src="./resources/ui/author_avatar.jpg" width="92" alt="Nyzeep avatar" />
</p>

<h1 align="center">LumiMate</h1>

<p align="center">
  一个安静、深邃、会呼吸的桌面 AI 陪伴空间。
</p>

<p align="center">
  <a href="https://github.com/Nyzeep/LumiMate"><img alt="Repository" src="https://img.shields.io/badge/repository-LumiMate-061125?style=flat-square&labelColor=09172E&color=E5A97F"></a>
  <img alt="Author" src="https://img.shields.io/badge/author-Nyzeep-061125?style=flat-square&labelColor=09172E&color=F2C39B">
  <img alt="Status" src="https://img.shields.io/badge/status-active%20prototype-061125?style=flat-square&labelColor=09172E&color=A8CFBC">
  <img alt="License" src="https://img.shields.io/badge/license-not%20specified-061125?style=flat-square&labelColor=09172E&color=8B7890">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-061125?style=flat-square&labelColor=09172E&color=E5A97F">
  <img alt="PySide6" src="https://img.shields.io/badge/PySide6-Qt%20Desktop-061125?style=flat-square&labelColor=09172E&color=F2C39B">
  <img alt="Qt WebEngine" src="https://img.shields.io/badge/Qt-WebEngine-061125?style=flat-square&labelColor=09172E&color=8B7890">
  <img alt="Vue 3" src="https://img.shields.io/badge/Vue-3-061125?style=flat-square&labelColor=09172E&color=A8CFBC">
  <img alt="Vite" src="https://img.shields.io/badge/Vite-frontend-061125?style=flat-square&labelColor=09172E&color=E5A97F">
</p>

## 项目信息

- 作者：`Nyzeep`
- 仓库：`https://github.com/Nyzeep/LumiMate`
- 技术栈：`Python + PySide6 + Qt WebEngine + QWebChannel + Vue 3 + Vite`
- 当前定位：本地化桌面 AI 陪伴应用原型

LumiMate 是一个围绕“空间化陪伴体验”构建的桌面 AI 项目。它不是普通工具式聊天窗口，而是一个以深蓝金色宇宙氛围、几何星空视觉语言和慢呼吸动效组成的数字意识空间。

Python 负责原生桌面窗口、系统桥接、模型加载、本地资源访问和运行时服务；Vue 3 负责完整视觉界面、九空间场景、动效系统、交互反馈和前端状态组织。

## 功能亮点

- 九个正式空间：首页、聊天空间、陪伴空间、工作台、加载空间、存储、设置、个性化、关于。
- WebEngine 混合架构：使用 `QWebEngineView` 承载现代 Web UI，同时保留 Python 的本地能力。
- QWebChannel 通信：前端通过桥接对象调用底层能力，不直接扫描路径或读写模型文件。
- 几何星空视觉系统：毛玻璃面板、极细 SVG 几何、琥珀辉光、轨道呼吸、环境星点与低频动效。
- 运行时 UI 引擎：统一管理场景切换、环境模式、动效偏好、诊断 HUD 和前端 ready 交接。
- 模型工作台：通过结构化模型卡片展示节点角色、标签、状态和加载过程，避免在主界面暴露原始路径。
- 作者信息与资源映射：项目地址、作者 Nyzeep、作者头像和背景资源都通过明确的配置与资产路径组织。

## 技术架构

### 桌面与后端层

- `Python 3.10+`
- `PySide6`
- `Qt WebEngine`
- `QWebChannel`

主要职责：

- 应用启动与环境检查
- 透明无边框桌面窗口
- 全屏 / 窗口化 / 最小化 / 关闭控制
- WebEngine 页面加载与启动遮罩
- 桥接对象注册与前后端通信
- 模型加载、路径扫描、文件 IO 与本地运行时服务

### 前端界面层

- `Vue 3`
- `Vite`
- CSS3 / SVG / Glassmorphism

主要职责：

- 九空间页面与场景切换
- 背景预加载与双层淡入
- 侧边导航、底部环境模式、抽屉、模型卡片与聊天输入
- 运行时环境动效、hover 稳定化和 reduced-motion 支持
- 开发诊断 HUD，包括 FPS、动画任务、RAF 任务和图层估算指标

### 桥接对象

当前前端通过 QWebChannel 使用的主要对象包括：

- `appBridge`：场景、背景、设置、项目元数据与环境模式
- `modelBridge`：模型目录、选择、加载、缓存释放、存储信息
- `chatBridge`：文本、语音、消息流和聊天状态
- `emotionBridge`：情绪、呼吸、存在感与倾听状态
- `companionBridge`：陪伴空间状态与渲染能力
- `windowBridge`：窗口控制与拖动辅助
- `shellBridge`：启动交接、boot phase 和前端 ready 信号

## 目录结构

```text
LumiMate/
├─ config/         运行配置、默认值、项目元数据与用户设置
├─ controllers/    控制器层，负责 UI 与服务之间的调度
├─ core/           启动、完整性检查、国际化和语音核心能力
├─ resources/      参考音频、作者头像与界面资源
├─ services/       模型加载、运行时服务和更新流程
├─ tools/          本地维护脚本
├─ ui/
│  ├─ assets/      资产清单与资源映射
│  ├─ bridge/      暴露给 QWebChannel 的 PySide6 桥接对象
│  ├─ qml/         冻结保留的旧 QML 回退层
│  └─ web/         Vue 3 WebEngine 前端工程
├─ 背景图片/        项目现有背景资源
├─ main.py         应用主入口
├─ run_lumi.bat    Windows 启动脚本
├─ requirements.txt Python 依赖列表
└─ README.md       项目说明文档
```

## 环境要求

建议准备：

- Windows 系统
- `Python 3.10` 或更高版本
- `Node.js` 与 `npm`
- 可用的 `pip`
- 支持 `PySide6 + Qt WebEngine` 的 Python 环境

完整语音和本地模型能力还需要准备对应模型、音频资源与推理环境。

## 快速开始

### 1. 创建虚拟环境

```powershell
python -m venv .venv
```

### 2. 安装 Python 依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. 安装并构建前端

```powershell
cd ui\web
npm install
npm run build
cd ..\..
```

应用正式启动时默认读取 `ui/web/dist/index.html`，因此首次运行前需要先完成前端构建。

### 4. 启动应用

```bat
run_lumi.bat
```

也可以直接运行：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 常用命令

```powershell
# 启动自检
.\.venv\Scripts\python.exe main.py --check

# 窗口模式启动，适合开发调试
.\.venv\Scripts\python.exe main.py --windowed

# 前端开发服务器
cd ui\web
npm run dev

# 前端生产构建
cd ui\web
npm run build
```

项目支持通过 `LUMIMATE_WEB_DEV_URL` 加载 Vite 开发服务器：

```powershell
$env:LUMIMATE_WEB_DEV_URL="http://127.0.0.1:5173"
.\.venv\Scripts\python.exe main.py --windowed
```

## 运行资源说明

LumiMate 的完整能力依赖部分本地运行资源，通常包括：

- `models/` 中的 ASR / LLM / TTS 模型资源
- `GenieData/` 相关语音或推理资源
- 某些模型栈需要的预编译依赖，例如 `flash_attn`
- `背景图片/` 中的项目背景图资源

这些大型运行时资源默认不会提交到仓库。新环境运行时，需要自行准备与当前功能匹配的模型和数据文件。

## 常见问题

### 启动时报找不到 PySide6 或 Qt WebEngine

请确认安装依赖时使用的 Python 解释器，与启动应用时使用的是同一个环境：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --check
```

### 启动时报找不到前端页面

请先生成前端构建产物：

```powershell
cd ui\web
npm install
npm run build
cd ..\..
```

### 语音或模型能力无法正常工作

这通常不是界面层问题，而是本地模型文件、语音资源、推理依赖或显卡环境未准备完整。请优先检查：

- 模型目录是否存在
- 语音资源是否完整
- Python 环境是否已安装所有依赖
- CUDA / 显卡 / 推理环境是否满足所用模型要求

## 开发建议

- 在 `controllers/` 中梳理业务入口和调用链
- 在 `services/` 中拆分模型、语音、更新等运行时职责
- 在 `ui/bridge/` 中统一前后端桥接协议
- 在 `ui/web/src/` 中继续维护场景、组件、动效和状态模块边界
- 为模型资源、用户配置、日志输出补齐更清晰的文档说明

## 注意事项

- 背景图使用项目内既有资源，不依赖外部下载路径。
- 前端只通过 QWebChannel 调用底层能力，不直接扫描路径或读写模型文件。
- 更新清单地址和项目仓库地址是两个不同概念，避免把 GitHub 首页当作自动更新 manifest。
- 当前仓库未看到明确的开源许可证文件；如果计划公开分发、接受外部贡献或用于商业场景，建议补充 `LICENSE` 文件并明确授权范围。
