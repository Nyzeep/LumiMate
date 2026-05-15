<h1 align="center">LumiMate</h1>

<p align="center">
  一个安静、会呼吸、带有空间感的桌面 AI 陪伴系统。
</p>

<p align="center">
  <img src="./resources/ui/lumi_home_stage.png" width="920" alt="LumiMate 运行界面预览" />
</p>

<p align="center">
  LumiMate 想做的不是“再开一个聊天窗口”，而是让你进入一个属于 Lumi 的数字空间：可以对话，可以陪伴，也可以用更直观的方式唤醒本地模型。
</p>

## 这是什么

LumiMate 是一款桌面端 AI Companion 应用。它把聊天、语音、模型管理和设置放进一套统一的空间化界面里，让用户打开程序时更像是进入一个安静的 AI 空间，而不是面对一组冰冷的配置面板。

它目前围绕五个主要空间组织体验：

- `Home`：欢迎、Lumi 状态、快速入口和今日情绪。
- `Chat`：文字对话、语音聆听、回复状态和呼吸式反馈。
- `Companion`：陪伴舞台，为后续 Live2D / Spine 或自定义角色扩展预留。
- `Workbench`：模型核心舱与星系选择，用视觉化方式扫描、下载、切换和加载模型。
- `Settings`：语言、启动、动效和基础系统设置。

## 你可以用它做什么

- 和 Lumi 进行本地 AI 对话。
- 使用 ASR / LLM / TTS 组成的本地模型链路。
- 在 Workbench 中扫描本地 `models/` 目录。
- 在“星系选择”中为 ASR 和 LLM 选择模型，并通过魔搭社区或 Hugging Face 下载。
- 加载、切换和释放模型缓存。
- 在深空风格的桌面界面里体验低频动效、情绪光效和空间化导航。

## 如何启动

如果你使用的是发布包或已经打包好的版本，通常只需要运行启动入口即可。LumiMate 会自动完成基础环境检查。

源码版当前入口是：

```powershell
python launcher.py
```

启动器会做这些事：

- 优先检测当前环境或项目 `.venv` 是否已经可用。
- 如果环境已经完整，会直接启动程序。
- 如果是首次运行且缺少依赖，会自动创建 `.venv` 并安装 `requirements.txt`。
- 检查界面构建产物是否存在。
- 启动 LumiMate 主程序。

开发时可以使用窗口模式：

```powershell
python launcher.py --windowed
```

也可以只做启动检查：

```powershell
python launcher.py --check
```

## 首次使用模型

LumiMate 会自动扫描本地模型目录：

```text
models/
├─ asr_model/
├─ llm_model/
└─ tts_model/
```

如果缺少 ASR 或 LLM，进入 `Workbench` 后可以打开“星系选择”。这里会显示可选模型来源：

- 魔搭社区：更适合中国社区用户。
- Hugging Face：适合网络条件允许或已有 HF 使用习惯的用户。

下载完成后，LumiMate 会把模型整理到对应目录，并自动重新扫描。TTS 目前保留为本地扫描和占位入口，后续会加入用户自行加载声线模型的流程。

## 推荐使用方式

第一次进入时，可以按这个顺序来：

1. 启动 LumiMate。
2. 进入 `Workbench`。
3. 如果提示缺少模型，打开“星系选择”。
4. 下载或放入 ASR / LLM / TTS 模型。
5. 点击加载模型，等待 Lumi 苏醒。
6. 回到 `Chat` 或 `Companion` 开始使用。

如果你只是想先看看界面，不准备立即加载大模型，也可以直接浏览各个空间。

## 运行要求

LumiMate 会自动处理 Python 虚拟环境和依赖安装，但完整模型能力仍然取决于本机环境：

- Windows 桌面环境。
- 可用的 Python 环境，打包版会尽量隐藏这一层。
- 足够的磁盘空间用于模型文件。
- 运行本地模型所需的 CPU / GPU / 显存条件。
- 可访问魔搭社区或 Hugging Face 的网络环境。

模型体积可能较大，首次下载会比较久，这是正常现象。

## 项目结构

```text
LumiMate/
├─ launcher.py              启动器，负责环境检测和启动
├─ main.py                  桌面程序入口
├─ config/                  应用配置和用户设置
├─ controllers/             主控制器
├─ services/                模型、下载、更新和运行服务
├─ core/                    启动、完整性检查和语音核心逻辑
├─ ui/
│  ├─ bridge/               Python 与界面之间的桥接层
│  ├─ web/                  Vue 前端界面
│  ├─ qml/                  QML 设计系统与备用空间资产
│  └─ assets/               界面资产清单
├─ resources/               预览图、参考音频和界面资源
└─ models/                  本地模型目录，通常不随仓库提交
```

## 技术说明

这部分是给开发者看的，普通用户不需要关心。

LumiMate 当前主要由这些部分组成：

- `Python`：启动器、本地服务、模型加载、语音链路和系统桥接。
- `PySide6 + Qt WebEngine`：桌面窗口、透明无边框外壳和 Web UI 承载。
- `QWebChannel`：前端与 Python 后端之间的通信。
- `Vue 3 + Vite`：主要界面、场景系统、动效和状态组织。
- `Transformers / Torch / Qwen ASR / Genie TTS`：本地模型与语音能力。
- `modelscope / huggingface_hub`：模型下载来源。

项目重点不是把技术名词堆出来，而是让这些能力最终服务于一个更有情绪和空间感的 AI 陪伴体验。

## 开发者入口

前端开发：

```powershell
cd ui\web
npm install
npm run dev
```

构建前端：

```powershell
cd ui\web
npm run build
```

使用 Vite 开发服务器启动桌面壳：

```powershell
$env:LUMIMATE_WEB_DEV_URL="http://127.0.0.1:5173"
python launcher.py --windowed
```

跳过启动器环境检查：

```powershell
$env:LUMIMATE_SKIP_BOOTSTRAP="1"
python main.py --windowed
```

## 当前状态

LumiMate 已经具备完整的桌面启动、空间化界面、模型扫描、模型下载入口和基础 AI 交互框架。后续重点会继续放在：

- 更完善的 TTS 自定义加载流程。
- 更稳定的模型下载与错误恢复。
- 更自然的陪伴舞台和角色表现。
- 更适合发布包的打包与安装体验。

LumiMate 的目标不是成为普通工具箱，而是成为一个有呼吸、有情绪、有空间感的 AI Companion System。
