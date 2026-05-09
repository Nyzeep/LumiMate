# LumiMate

LumiMate 是一个基于 Python 和 PyQt6 的桌面 AI Companion 应用。当前版本包含“Quiet Geometric Emotionalism”夜间情绪空间 UI、语音/文字最小对话入口、模型唤醒工作台，以及面向后续角色资源接入的界面结构。

## 运行

建议先创建虚拟环境并安装依赖：

```powershell
python -m venv ..\.venv
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

启动应用：

```bat
run_lumi.bat
```

也可以直接运行：

```powershell
python main.py
```

`run_lumi.bat` 会优先使用项目上一级的 `D:\Pycharm_Code\.venv`，如果不存在才回退到项目根目录下的 `.venv`、系统 `python` 或 `py -3`。

## 目录

```text
config/       应用配置与默认模型路径
controllers/  UI 与服务层控制器
core/         语音助手核心调用
services/     模型加载与运行生命周期
ui/           PyQt6 界面、组件、页面、主题与效果
resources/    参考音频与 UI 位图资产
tools/        项目维护脚本，例如 UI 资产生成脚本
```

`resources/ui/` 中的三张 PNG 是项目内原创生成资产，用于 Lumi 夜间场景、陪伴立绘和氛围纹理；可通过 `tools/generate_ui_assets.py` 重新生成。

`resources/prompt_wav.json` 用于配置默认 TTS 参考音频和参考文本，工作台会在启动时读取它并填入模型初始化参数。

## 额外运行依赖

模型加载阶段还依赖本地可用的 ASR / TTS 包，例如 `qwen_asr` 和 `genie_tts`，以及对应模型文件。若只启动界面，安装 `requirements.txt` 即可；若要完整语音对话，请确认 `models/`、`GenieData/` 和 TTS 预编译资源路径齐全。

以下目录通常包含本地模型、运行数据或大型预编译依赖，默认不会提交到 Git：

- `GenieData/`
- `models/`
- `预编译的flash atn/`
