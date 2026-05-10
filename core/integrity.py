from __future__ import annotations

import hashlib
import json
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
    "ui/qml/Main.qml",
    "ui/qml/layouts/RootScene.qml",
    "ui/qml/layouts/SpatialRouter.qml",
    "ui/qml/themes/Theme.qml",
    "ui/qml/animations/MotionRuntime.qml",
    "ui/qml/effects/DeepSpaceBackground.qml",
    "ui/qml/effects/ShaderHost.qml",
    "ui/qml/geometry/OrbitalField.qml",
    "ui/qml/particles/ParticleMist.qml",
    "ui/qml/transitions/SceneShift.qml",
    "ui/qml/scenes/SceneRegistry.qml",
    "ui/qml/components/AmbientPlayerDock.qml",
    "ui/qml/components/LunarGateStage.qml",
    "ui/qml/components/MemoryPanel.qml",
    "ui/qml/components/ReferenceActionNode.qml",
    "ui/qml/components/ReferenceNavNode.qml",
    "ui/qml/components/ReferenceSideRail.qml",
    "ui/qml/components/StatusOrbitCard.qml",
    "ui/qml/components/TopWindowControls.qml",
    "ui/qml/components/OrbitNodeButton.qml",
    "ui/qml/components/SpatialInput.qml",
    "ui/qml/components/PresenceText.qml",
    "ui/qml/components/ModelRitualProgress.qml",
    "ui/qml/components/CompanionStage.qml",
    "ui/qml/pages/HomeSpace.qml",
    "ui/qml/pages/ChatSpace.qml",
    "ui/qml/pages/CompanionSpace.qml",
    "ui/qml/pages/WorkbenchSpace.qml",
    "ui/qml/pages/SettingsSpace.qml",
    "ui/qml/pages/AboutSpace.qml",
    "ui/assets/asset_manifest.json",
]


class IntegrityVerifier:
    def __init__(self, root: Path | None = None, manifest_path: Path | None = None):
        self.root = root or ProjectPaths().root
        self.manifest_path = manifest_path or self.root / "config" / "integrity_manifest.json"

    def verify(self) -> list[str]:
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return [f"Integrity manifest missing: {self.manifest_path}"]
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            return [f"Integrity manifest unreadable: {exc}"]

        files = manifest.get("files", {})
        if not isinstance(files, dict):
            return ["Integrity manifest has invalid file map."]

        issues: list[str] = []
        for relative_path, expected_hash in files.items():
            path = self.root / str(relative_path)
            if not path.exists():
                issues.append(f"Core file missing: {relative_path}")
                continue
            try:
                actual_hash = sha256_file(path)
            except OSError as exc:
                issues.append(f"Core file unreadable: {relative_path} ({exc})")
                continue
            if actual_hash != expected_hash:
                issues.append(f"Core file changed: {relative_path}")
        return issues


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
