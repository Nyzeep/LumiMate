# LumiMate

LumiMate 是一个基于 Python 与 PyQt6 构建的桌面 AI Companion 应用。

它的目标不是做传统 AI 控制台，而是提供一个安静、沉浸、带有情绪氛围的数字陪伴空间。当前版本包含诗性化的桌面 UI、语音对话入口、模型工作台，以及面向未来 Live2D / Spine 角色接入的陪伴空间架构。

## 功能概览

- PyQt6 无边框桌面窗口
- 代码绘制的静夜梦境背景与 Companion 场景
- 首页、对话、陪伴、工作台、设置五页结构
- ASR / LLM / TTS 模型加载生命周期管理
- 语音对话启动、停止与日志反馈
- 面向 Live2D / Spine 的 UI 预留结构

## 运行方式

建议使用项目虚拟环境运行：

```bat
run_lumi.bat
```

或手动执行：

```powershell
python main.py
```

## 目录说明

```text
config/       应用配置与默认模型路径
controllers/  UI 与服务层控制器
core/         语音助手核心调用
services/     模型加载与运行生命周期
ui/           PyQt6 界面、组件、页面、主题与效果
resources/    参考音频等轻量资源
```

## 注意

以下目录包含本地模型、运行数据或大型预编译依赖，默认不会提交到 Git：

- `GenieData/`
- `models/`
- `预编译的flash atn/`
