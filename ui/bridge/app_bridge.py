from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot

from config import APP_AUTHOR, APP_PHILOSOPHY, APP_VERSION, PROJECT_ROOT, UPDATE_MANIFEST_URL, UserSettings
from core.i18n import tr

SCENE_GROUPS = [
    {
        "id": "scene_group_core",
        "labelKey": "nav.group.core",
        "subtitleKey": "nav.group.core.subtitle",
        "scenes": [
            {
                "id": "home",
                "labelKey": "nav.home",
                "titleKey": "scene.home.title",
                "titleEn": "Home Space",
                "component": "HomeScene.qml",
                "backgroundAsset": "background2",
                "icon": "△",
            },
            {
                "id": "chat",
                "labelKey": "nav.chat",
                "titleKey": "scene.chat.title",
                "titleEn": "Chat Space",
                "component": "ChatScene.qml",
                "backgroundAsset": "background3",
                "icon": "◌",
            },
            {
                "id": "companion",
                "labelKey": "nav.companion",
                "titleKey": "scene.companion.title",
                "titleEn": "Companion Space",
                "component": "CompanionScene.qml",
                "backgroundAsset": "background4",
                "icon": "✦",
            },
        ],
    },
    {
        "id": "scene_group_runtime",
        "labelKey": "nav.group.runtime",
        "subtitleKey": "nav.group.runtime.subtitle",
        "scenes": [
            {
                "id": "workbench",
                "labelKey": "nav.workbench",
                "titleKey": "scene.workbench.title",
                "titleEn": "Workbench",
                "component": "WorkbenchScene.qml",
                "backgroundAsset": "background1",
                "icon": "◈",
            },
            {
                "id": "loading",
                "labelKey": "nav.loading",
                "titleKey": "scene.loading.title",
                "titleEn": "Loading Space",
                "component": "LoadingScene.qml",
                "backgroundAsset": "background1",
                "icon": "◎",
            },
            {
                "id": "storage",
                "labelKey": "nav.storage",
                "titleKey": "scene.storage.title",
                "titleEn": "Storage",
                "component": "StorageScene.qml",
                "backgroundAsset": "background1",
                "icon": "⬡",
            },
        ],
    },
    {
        "id": "scene_group_inner",
        "labelKey": "nav.group.inner",
        "subtitleKey": "nav.group.inner.subtitle",
        "scenes": [
            {
                "id": "settings",
                "labelKey": "nav.settings",
                "titleKey": "scene.settings.title",
                "titleEn": "Settings",
                "component": "SettingsScene.qml",
                "backgroundAsset": "background3",
                "icon": "⌘",
            },
            {
                "id": "personality",
                "labelKey": "nav.personality",
                "titleKey": "scene.personality.title",
                "titleEn": "Personality",
                "component": "PersonalityScene.qml",
                "backgroundAsset": "background3",
                "icon": "◇",
            },
            {
                "id": "about",
                "labelKey": "nav.about",
                "titleKey": "scene.about.title",
                "titleEn": "About Lumi",
                "component": "AboutScene.qml",
                "backgroundAsset": "background1",
                "icon": "☉",
            },
        ],
    },
]

SCENE_LOOKUP: dict[str, dict] = {}
DEFAULT_SCENES_BY_GROUP: dict[int, str] = {}
for group_index, group in enumerate(SCENE_GROUPS):
    DEFAULT_SCENES_BY_GROUP[group_index] = group["scenes"][0]["id"]
    for scene_index, scene in enumerate(group["scenes"]):
        SCENE_LOOKUP[scene["id"]] = {
            **scene,
            "groupIndex": group_index,
            "groupId": group["id"],
            "groupLabelKey": group["labelKey"],
            "groupSubtitleKey": group["subtitleKey"],
            "sceneIndex": scene_index,
        }

VALID_SCENES = set(SCENE_LOOKUP)
SCENE_IDS = [scene["id"] for group in SCENE_GROUPS for scene in group["scenes"]]


class AppBridge(QObject):
    currentPageChanged = Signal()
    currentSceneGroupChanged = Signal()
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
        current_meta = SCENE_LOOKUP[self._current_page]
        self._current_scene_group_index = int(current_meta["groupIndex"])
        self._last_scene_by_group = dict(DEFAULT_SCENES_BY_GROUP)
        self._last_scene_by_group[self._current_scene_group_index] = self._current_page
        self._language_revision = 0
        self._asset_manifest = self._load_asset_manifest()

    @Property(str, notify=currentPageChanged)
    def currentPage(self) -> str:
        return self._current_page

    @Property(int, notify=currentSceneGroupChanged)
    def currentSceneGroupIndex(self) -> int:
        return self._current_scene_group_index

    @Property("QVariantList", notify=currentSceneGroupChanged)
    def currentSceneGroupScenes(self):
        return SCENE_GROUPS[self._current_scene_group_index]["scenes"]

    @Property(str, notify=currentSceneGroupChanged)
    def currentSceneGroupLabelKey(self) -> str:
        return SCENE_GROUPS[self._current_scene_group_index]["labelKey"]

    @Property(str, notify=currentSceneGroupChanged)
    def currentSceneGroupSubtitleKey(self) -> str:
        return SCENE_GROUPS[self._current_scene_group_index]["subtitleKey"]

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
        return self._normalize_scene(self._settings.startup_page)

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
        return SCENE_IDS

    @Property("QVariantList", constant=True)
    def sceneGroups(self):
        return SCENE_GROUPS

    @Slot(str)
    def navigate(self, page: str) -> None:
        page = self._normalize_scene(page.strip())
        target_meta = SCENE_LOOKUP[page]
        group_changed = int(target_meta["groupIndex"]) != self._current_scene_group_index
        self._current_scene_group_index = int(target_meta["groupIndex"])
        self._last_scene_by_group[self._current_scene_group_index] = page
        if page == self._current_page:
            if group_changed:
                self.currentSceneGroupChanged.emit()
            return
        self._current_page = page
        self.currentPageChanged.emit()
        if group_changed:
            self.currentSceneGroupChanged.emit()

    @Slot(int)
    def setSceneGroup(self, group_index: int) -> None:
        if group_index < 0 or group_index >= len(SCENE_GROUPS):
            return
        target_scene = self._last_scene_by_group.get(group_index, DEFAULT_SCENES_BY_GROUP[group_index])
        self.navigate(target_scene)

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

    @Slot(str, result=str)
    def sceneComponent(self, scene_id: str) -> str:
        return str(SCENE_LOOKUP.get(self._normalize_scene(scene_id), {}).get("component", "HomeScene.qml"))

    @Slot(str, result=str)
    def sceneBackgroundAsset(self, scene_id: str) -> str:
        return str(SCENE_LOOKUP.get(self._normalize_scene(scene_id), {}).get("backgroundAsset", "background2"))

    @Slot(str, result=str)
    def sceneBackgroundUrl(self, scene_id: str) -> str:
        return self.assetUrl(self.sceneBackgroundAsset(scene_id))

    @Slot(str, result="QVariantMap")
    def sceneMeta(self, scene_id: str):
        return SCENE_LOOKUP.get(self._normalize_scene(scene_id), SCENE_LOOKUP["home"])

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
