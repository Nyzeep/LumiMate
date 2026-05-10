# LumiMate

LumiMate is a desktop AI companion built as a spatial emotional system. The current runtime uses `Python + PySide6 + Qt Quick/QML` and presents five primary spaces: `Home`, `Chat`, `Companion`, `Workbench`, and `Settings`.

## Run

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Launch the app:

```bat
run_lumi.bat
```

Or run directly:

```powershell
python main.py
```

## Structure

```text
config/       Runtime config, defaults, and user settings
controllers/  UI-to-service controller flow
core/         Bootstrap, integrity, i18n, and voice assistant core
services/     Model loading, runtime service, and updater
ui/bridge/    PySide6 bridge objects exposed to QML
ui/qml/       Scene runtime, design system, components, shaders
resources/    Reference audio and visual assets
tools/        Local maintenance scripts
```

## UI Runtime

The spatial UI is centered on:

- `ui/qml/scenes/` for the five primary spaces
- `ui/qml/components/` for reusable ritual/orbit/glass primitives
- `ui/qml/design_system/` for color, type, motion, geometry, and depth
- `ui/qml/shaders/` for future GPU passes with graceful fallback

`Workbench` scans the local `models/` tree automatically and exposes ASR, LLM, and TTS candidates as visual nodes instead of manual path fields.

## Runtime Dependencies

Model loading still depends on local ASR / TTS packages and local model assets. For full voice interaction, make sure these are present:

- `models/`
- `GenieData/`
- any required precompiled `flash_attn` resources
