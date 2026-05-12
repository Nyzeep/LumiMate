# LumiMate

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt_for_Python-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![QtWebEngine](https://img.shields.io/badge/QtWebEngine-Web_Runtime-0D1117?style=for-the-badge&logo=qt&logoColor=41CD52)
![Vue 3](https://img.shields.io/badge/Vue-3-42B883?style=for-the-badge&logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![QWebChannel](https://img.shields.io/badge/QWebChannel-Bridge-FF6A3D?style=for-the-badge)

一个以“空间情绪系统”为核心概念的桌面 AI 陪伴应用。  
项目采用 `Python + PySide6 + Qt WebEngine + Vue 3` 的混合架构：Python 负责桌面窗口、业务控制、运行时服务与桥接能力，Web 前端负责沉浸式界面、视觉表达与交互体验。

</div>

---

## 项目简介

LumiMate 是一个桌面端 AI 陪伴项目，当前版本通过 `PySide6` 承载原生桌面窗口，通过 `QWebEngineView` 加载 `Vue 3` 构建的前端界面，并借助 `QWebChannel` 在 Python 与前端之间建立通信桥梁。

这套架构的目标很明确：

- 保留 Python 在本地资源访问、模型调度、系统能力调用方面的优势
- 保留 Web 技术在视觉设计、动画表现、界面迭代方面的高效率
- 让桌面应用拥有更灵活的 AI 交互界面与更强的沉浸式表达能力

从当前代码结构来看，项目已经具备以下基础能力：

- 桌面窗口启动与全屏/窗口化切换
- 本地 Web 前端构建与嵌入式加载
- Python 与前端桥接通信
- 模型、对话、情绪、角色陪伴等多桥接对象挂载
- 本地语音相关依赖接入基础
- 背景资源与运行配置分层组织

---

## 技术架构

### 后端与桌面层

- `Python 3.10+`
- `PySide6`
- `Qt WebEngine`
- `QWebChannel`

主要负责：

- 应用启动与环境检查
- 原生窗口管理
- WebEngine 页面加载
- 前后端桥接对象注册
- 控制器与服务层调度
- 本地模型与资源访问

### 前端界面层

- `Vue 3`
- `Vite`

主要负责：

- 空间化首页与沉浸式界面展示
- 页面状态管理与视觉反馈
- 与 Python 桥接对象进行交互
- 背景资源、聊天界面、情绪界面等前端表现层能力

### AI 与音频相关依赖

根据当前 `requirements.txt`，项目已接入或预留以下运行依赖：

- `transformers`
- `accelerate`
- `torch`
- `torchaudio`
- `qwen-asr`
- `genie-tts`
- `sounddevice`
- `numpy`

这说明项目面向的是本地推理 / 本地语音交互能力较强的桌面 AI 场景，而不只是一个单纯的界面壳层。

---

## 目录结构

```text
LumiMate/
├─ config/         运行配置、默认参数、用户设置
├─ controllers/    控制器层，负责 UI 与服务之间的调度
├─ core/           启动、环境检查、基础核心能力
├─ resources/      项目资源文件
├─ services/       运行时服务、模型加载、更新等逻辑
├─ tools/          本地维护脚本
├─ ui/
│  ├─ assets/      前端或界面资源
│  ├─ bridge/      暴露给 QWebChannel 的桥接对象
│  ├─ qml/         旧版或保留的 QML 相关内容
│  └─ web/         Vue 3 前端工程
├─ 背景图片/        项目使用的背景图资源
├─ main.py         应用主入口
├─ run_lumi.bat    Windows 启动脚本
├─ requirements.txt Python 依赖列表
└─ README.md       项目说明文档
```

---

## 运行机制说明

项目入口位于 `main.py`，核心启动流程大致如下：

1. 检查运行环境是否满足要求
2. 确认前端构建产物 `ui/web/dist/index.html` 是否存在
3. 初始化 `QApplication`
4. 创建透明、无边框的主窗口
5. 创建 `QWebEngineView` 加载前端页面
6. 注册多个桥接对象到 `QWebChannel`
7. 根据启动参数决定全屏显示或窗口化显示

当前代码里可以确认的桥接对象包括：

- `appBridge`
- `modelBridge`
- `chatBridge`
- `emotionBridge`
- `companionBridge`
- `windowBridge`

这意味着前端并不是独立运行的普通网页，而是通过桥接层与 Python 端深度协作的桌面应用界面。

---

## 环境要求

在开始运行前，建议准备以下环境：

- Windows 系统
- `Python 3.10` 或更高版本
- 可用的 `pip`
- `Node.js` 与 `npm`
- 支持 `PySide6 + QtWebEngine` 的本地 Python 环境

如果你要完整启用本地语音或模型能力，还需要额外准备项目运行所需的大型模型资源与语音资源。

---

## 快速开始

### 1. 创建虚拟环境

```powershell
python -m venv .venv
```

### 2. 安装 Python 依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果你没有使用虚拟环境，也可以使用当前 Python 解释器安装，但更推荐隔离环境运行。

### 3. 安装前端依赖并构建

```powershell
cd ui\web
npm install
npm run build
cd ..\..
```

应用正式启动时默认读取的是构建后的静态页面，因此这一步是必须的。

### 4. 启动项目

推荐直接使用批处理脚本启动：

```bat
run_lumi.bat
```

也可以直接运行主入口：

```powershell
python main.py
```

---

## 启动方式

### 默认启动

```powershell
python main.py
```

默认会以全屏方式显示主界面。

### 窗口模式启动

```powershell
python main.py --windowed
```

这个模式更适合开发调试，当前代码中会将窗口尺寸设置为 `1600 x 900`。

### 启动自检

```powershell
python main.py --check
```

这个命令会检查：

- 当前解释器是否可用
- 前端构建产物是否存在
- LumiMate 的 WebEngine 启动前置条件是否满足

---

## 前端开发说明

前端工程位于 `ui/web/`，使用 `Vue 3 + Vite` 构建。

常用命令如下：

```powershell
cd ui\web
npm install
npm run dev
```

当前 `package.json` 中提供的脚本有：

- `npm run dev`：本地开发服务器
- `npm run build`：构建生产版本
- `npm run preview`：本地预览构建结果

项目中还预留了 `LUMIMATE_WEB_DEV_URL` 环境变量：  
当这个环境变量被设置时，桌面端会优先加载该地址，而不是本地 `dist/index.html`。这对联调前端开发服务器非常有用。

示例思路如下：

```powershell
$env:LUMIMATE_WEB_DEV_URL="http://127.0.0.1:5173"
python main.py --windowed
```

---

## 批处理启动脚本说明

`run_lumi.bat` 已经帮你处理了一些常见情况：

- 优先使用项目内的 `.venv\Scripts\python.exe`
- 如果项目内没有虚拟环境，则尝试使用系统 `python`
- 如果系统没有 `python`，则继续尝试 `py -3`

也就是说，对于 Windows 用户来说，只要环境准备完成，直接双击或命令行运行 `run_lumi.bat` 就可以更稳定地启动项目。

---

## 运行资源说明

从现有代码和依赖来看，LumiMate 除了仓库内代码外，还依赖一部分本地运行资源，通常包括但不限于：

- `models/` 目录中的模型文件
- `GenieData/` 一类语音或推理相关资源
- 某些预编译依赖资源，例如 `flash_attn` 相关内容

这些大体积资源通常不会直接提交到仓库，因此如果你在新环境中运行项目，需要自行准备与当前功能匹配的模型和数据文件。

---

## 适合谁使用这个项目

如果你正在做以下方向，这个项目会很有参考价值：

- 桌面 AI 助手
- 本地大模型陪伴应用
- 语音交互型桌面程序
- 使用 Web 技术构建桌面原生 UI 的混合应用
- 基于 PySide6 的可视化 AI 产品原型

---

## 常见问题

### 1. 启动时报找不到 PySide6 或 QtWebEngine

请确认你安装依赖时使用的 Python 解释器，与实际启动项目时使用的是同一个环境。

建议优先执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --check
```

### 2. 启动时报找不到前端页面

说明 `ui/web/dist/index.html` 尚未生成，请先执行：

```powershell
cd ui\web
npm install
npm run build
cd ..\..
```

### 3. 语音或模型能力无法正常工作

这通常不是界面层问题，而是本地模型文件、语音资源或相关依赖未准备完整。请优先检查：

- 模型目录是否存在
- 语音资源是否完整
- 当前 Python 环境是否已安装所有依赖
- 显卡 / CUDA / 推理环境是否满足你所用模型的要求

---

## 开发建议

如果你准备继续扩展 LumiMate，建议优先从以下方向入手：

- 在 `controllers/` 中梳理业务入口与调用链
- 在 `services/` 中拆分模型、语音、更新等运行时职责
- 在 `ui/bridge/` 中统一前后端桥接协议
- 在 `ui/web/src/` 中完善界面状态与交互逻辑
- 为模型资源、用户配置、日志输出补齐更清晰的文档说明

---

## 项目状态

当前仓库已经具备清晰的桌面应用骨架、前后端混合运行结构，以及 AI 应用继续扩展所需的基本技术路线。  
如果后续继续完善模型接入、语音链路、角色系统与场景化界面，LumiMate 会很适合作为一个本地化桌面 AI 陪伴产品原型持续演进。

---

## License

当前仓库中未看到明确的开源许可证文件。  
如果你计划公开分发、接受外部贡献或用于商业场景，建议尽快补充 `LICENSE` 文件并明确授权范围。
