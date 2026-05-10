from __future__ import annotations

from pathlib import Path

from config import ProjectPaths


DEFAULT_CORE_FILES = [
    "main.py",
    "config/app_config.py",
    "core/bootstrap.py",
    "core/integrity.py",
    "core/i18n.py",
    "controllers/main_controller.py",
    "services/assistant_service.py",
    "services/model_manager.py",
    "services/update_service.py",
    "core/voice_assistant.py",
    "ui/bridge/app_bridge.py",
    "ui/bridge/model_bridge.py",
    "ui/bridge/chat_bridge.py",
    "ui/bridge/emotion_bridge.py",
    "ui/bridge/companion_bridge.py",
    "ui/qml/main.qml",
]


class IntegrityVerifier:
    def __init__(self, root: Path | None = None, manifest_path: Path | None = None):
        self.root = root or ProjectPaths().root
        self.manifest_path = manifest_path

    def verify(self) -> list[str]:
        issues: list[str] = []
        for relative_path in DEFAULT_CORE_FILES:
            path = self.root / relative_path
            if not path.exists():
                issues.append(f"Core file missing: {relative_path}")
        return issues
