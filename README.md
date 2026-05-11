# LumiMate

LumiMate is a desktop AI companion built as a spatial emotional system. The current runtime uses `Python + PySide6 + QWebEngineView + Vue 3`, with Python owning the backend logic and the web layer owning all visual rendering.

## Run

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Build the WebEngine frontend:

```powershell
cd ui\web
npm install
npm run build
cd ..\..
```

Launch the app:

```bat
run_lumi.bat
```

Or run directly:

```powershell
python main.py
```

For a windowed development launch instead of fullscreen:

```powershell
python main.py --windowed
```

## Structure

```text
config/       Runtime config, defaults, and user settings
controllers/  UI-to-service controller flow
core/         Bootstrap, integrity, i18n, and voice assistant core
services/     Model loading, runtime service, and updater
ui/bridge/    PySide6 bridge objects exposed to QWebChannel
ui/web/       Vue 3 WebEngine frontend
ui/qml/       Legacy QML runtime kept temporarily as a fallback
resources/    Reference audio and visual assets
tools/        Local maintenance scripts
```

## UI Runtime

The spatial UI is centered on:

- `main.py` for the transparent frameless WebEngine container
- `ui/bridge/` for QWebChannel objects used by the frontend
- `ui/web/src/` for the Vue home space, global visual system, and SVG geometric interface
- `背景图片/` for the existing project backgrounds; the frontend selects them through `appBridge`

The hybrid architecture keeps the background assets in Python-controlled mappings while the WebEngine frontend renders the full glassmorphism interface.

## Runtime Dependencies

Model loading still depends on local ASR / TTS packages and local model assets. For full voice interaction, make sure these are present:

- `models/`
- `GenieData/`
- any required precompiled `flash_attn` resources
