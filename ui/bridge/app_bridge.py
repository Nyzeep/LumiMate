from __future__ import annotations

import json
import sys
from pathlib import Path

from PyQt6.QtCore import QObject, QUrl, pyqtProperty, pyqtSignal, pyqtSlot

from config import APP_AUTHOR, APP_PHILOSOPHY, APP_VERSION, PROJECT_ROOT, UPDATE_MANIFEST_URL, UserSettings
from core.i18n import tr


class AppBridge(QObject):
    currentPageChanged = pyqtSignal()
    languageChanged = pyqtSignal()
    languageRevisionChanged = pyqtSignal()
    settingsChanged = pyqtSignal()
    updateRequested = pyqtSignal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._settings = UserSettings.load()
        if self._settings.language not in {"zh-CN", "en-US"}:
            self._settings.language = "zh-CN"
        self._current_page = self._settings.startup_page if self._settings.startup_page else "home"
        self._language_revision = 0
        self._asset_manifest = self._load_asset_manifest()

    @pyqtProperty(str, notify=currentPageChanged)
    def currentPage(self) -> str:
        return self._current_page

    @pyqtProperty(str, notify=languageChanged)
    def language(self) -> str:
        return self._settings.language

    @pyqtProperty(int, notify=languageRevisionChanged)
    def languageRevision(self) -> int:
        return self._language_revision

    @pyqtProperty(bool, notify=settingsChanged)
    def checkUpdateOnStartup(self) -> bool:
        return self._settings.check_update_on_startup

    @pyqtProperty(str, notify=settingsChanged)
    def startupPage(self) -> str:
        return self._settings.startup_page

    @pyqtProperty(str, constant=True)
    def appVersion(self) -> str:
        return APP_VERSION

    @pyqtProperty(str, constant=True)
    def appAuthor(self) -> str:
        return APP_AUTHOR

    @pyqtProperty(str, constant=True)
    def appPhilosophy(self) -> str:
        return APP_PHILOSOPHY

    @pyqtProperty(str, constant=True)
    def projectRoot(self) -> str:
        return str(PROJECT_ROOT)

    @pyqtProperty(str, constant=True)
    def pythonExecutable(self) -> str:
        return sys.executable

    @pyqtProperty(str, constant=True)
    def updateSource(self) -> str:
        return UPDATE_MANIFEST_URL or "Not configured"

    @pyqtSlot(str)
    def navigate(self, page: str) -> None:
        page = page.strip()
        if not page or page == self._current_page:
            return
        self._current_page = page
        self.currentPageChanged.emit()

    @pyqtSlot(str, bool, str)
    def saveSettings(self, language: str, check_update_on_startup: bool, startup_page: str) -> None:
        self._set_language(language or "zh-CN")
        self._settings.check_update_on_startup = bool(check_update_on_startup)
        self._settings.startup_page = startup_page or "home"
        self._settings.save()
        self.settingsChanged.emit()

    @pyqtSlot(str)
    def setLanguage(self, language: str) -> None:
        self._set_language(language or "zh-CN")
        self._settings.save()

    @pyqtSlot(str, str, result=str)
    def t(self, key: str, language: str) -> str:
        return tr(key, language or self._settings.language)

    @pyqtSlot()
    def checkUpdates(self) -> None:
        self.updateRequested.emit()
        self._controller.check_updates()

    @pyqtSlot(str, result=str)
    def assetUrl(self, name: str) -> str:
        relative = self._asset_manifest.get(name, "")
        if not relative:
            return ""
        path = (PROJECT_ROOT / relative).resolve()
        return QUrl.fromLocalFile(str(path)).toString()

    @pyqtSlot(str, result=bool)
    def assetExists(self, name: str) -> bool:
        relative = self._asset_manifest.get(name, "")
        return bool(relative and (PROJECT_ROOT / relative).exists())

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
