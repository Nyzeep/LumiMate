from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot

from config import APP_AUTHOR, APP_PHILOSOPHY, APP_VERSION, PROJECT_ROOT, UPDATE_MANIFEST_URL, UserSettings
from core.i18n import tr


VALID_SCENES = {"home", "chat", "companion", "workbench", "settings"}


class AppBridge(QObject):
    currentPageChanged = Signal()
    languageChanged = Signal()
    languageRevisionChanged = Signal()
    settingsChanged = Signal()
    updateRequested = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._settings = UserSettings.load()
        if self._settings.language not in {"zh-CN", "en-US"}:
            self._settings.language = "zh-CN"
        self._current_page = self._normalize_scene(self._settings.startup_page)
        self._language_revision = 0
        self._asset_manifest = self._load_asset_manifest()

    @Property(str, notify=currentPageChanged)
    def currentPage(self) -> str:
        return self._current_page

    @Property(str, notify=languageChanged)
    def language(self) -> str:
        return self._settings.language

    @Property(int, notify=languageRevisionChanged)
    def languageRevision(self) -> int:
        return self._language_revision

    @Property(bool, notify=settingsChanged)
    def checkUpdateOnStartup(self) -> bool:
        return self._settings.check_update_on_startup

    @Property(str, notify=settingsChanged)
    def startupPage(self) -> str:
        return self._settings.startup_page

    @Property(bool, notify=settingsChanged)
    def reduceMotion(self) -> bool:
        return self._settings.reduce_motion

    @Property(str, constant=True)
    def appVersion(self) -> str:
        return APP_VERSION

    @Property(str, constant=True)
    def appAuthor(self) -> str:
        return APP_AUTHOR

    @Property(str, constant=True)
    def appPhilosophy(self) -> str:
        return APP_PHILOSOPHY

    @Property(str, constant=True)
    def projectRoot(self) -> str:
        return str(PROJECT_ROOT)

    @Property(str, constant=True)
    def pythonExecutable(self) -> str:
        return sys.executable

    @Property(str, constant=True)
    def updateSource(self) -> str:
        return UPDATE_MANIFEST_URL or "Not configured"

    @Property("QVariantList", constant=True)
    def sceneIds(self):
        return ["home", "chat", "companion", "workbench", "settings"]

    @Slot(str)
    def navigate(self, page: str) -> None:
        page = self._normalize_scene(page.strip())
        if page == self._current_page:
            return
        self._current_page = page
        self.currentPageChanged.emit()

    @Slot(str, bool, str, bool)
    def saveSettings(self, language: str, check_update_on_startup: bool, startup_page: str, reduce_motion: bool) -> None:
        self._set_language(language or "zh-CN")
        self._settings.check_update_on_startup = bool(check_update_on_startup)
        self._settings.startup_page = self._normalize_scene(startup_page)
        self._settings.reduce_motion = bool(reduce_motion)
        self._settings.save()
        self.settingsChanged.emit()

    @Slot(str)
    def setLanguage(self, language: str) -> None:
        self._set_language(language or "zh-CN")
        self._settings.save()

    @Slot(str, str, result=str)
    def t(self, key: str, language: str) -> str:
        return tr(key, language or self._settings.language)

    @Slot()
    def checkUpdates(self) -> None:
        self.updateRequested.emit()
        self._controller.check_updates()

    @Slot(str, result=str)
    def assetUrl(self, name: str) -> str:
        relative = self._asset_manifest.get(name, "")
        if not relative:
            return ""
        path = (PROJECT_ROOT / relative).resolve()
        return QUrl.fromLocalFile(str(path)).toString()

    @Slot(str, result=bool)
    def assetExists(self, name: str) -> bool:
        relative = self._asset_manifest.get(name, "")
        return bool(relative and (PROJECT_ROOT / relative).exists())

    def _normalize_scene(self, scene: str) -> str:
        return scene if scene in VALID_SCENES else "home"

    def _load_asset_manifest(self) -> dict[str, str]:
        manifest = PROJECT_ROOT / "ui" / "assets" / "asset_manifest.json"
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            assets = payload.get("assets", {})
            if isinstance(assets, dict):
                return {str(key): str(value) for key, value in assets.items()}
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return {}
        return {}

    def _set_language(self, language: str) -> None:
        language = language if language in {"zh-CN", "en-US"} else "zh-CN"
        if language == self._settings.language:
            return
        self._settings.language = language
        self._language_revision += 1
        self.languageChanged.emit()
        self.languageRevisionChanged.emit()
