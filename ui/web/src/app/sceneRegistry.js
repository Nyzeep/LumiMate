import background1 from "../../../../背景图片/背景1.png";
import background2 from "../../../../背景图片/背景2.png";
import background3 from "../../../../背景图片/背景3.png";
import background4 from "../../../../背景图片/背景4.png";
import authorAvatar from "../../../../resources/ui/author_avatar.jpg";
import AboutScene from "../scenes/AboutScene.vue";
import ChatScene from "../scenes/ChatScene.vue";
import CompanionScene from "../scenes/CompanionScene.vue";
import HomeScene from "../scenes/HomeScene.vue";
import LoadingScene from "../scenes/LoadingScene.vue";
import PersonalityScene from "../scenes/PersonalityScene.vue";
import SettingsScene from "../scenes/SettingsScene.vue";
import StorageScene from "../scenes/StorageScene.vue";
import WorkbenchScene from "../scenes/WorkbenchScene.vue";

export const ASSET_URLS = {
  background1,
  background2,
  background3,
  background4,
  authorAvatar
};

export const ICON_PATHS = {
  home: "M12 5.5 18 16H6Z",
  chat: "M12 7.2a4.8 4.8 0 1 1 0 9.6 4.8 4.8 0 0 1 0-9.6Z",
  companion: "M12 4.5 14.3 9.7 19.5 12 14.3 14.3 12 19.5 9.7 14.3 4.5 12 9.7 9.7Z",
  workbench: "m12 4.5 7 7.5-7 7.5L5 12Z",
  loading: "M12 5a7 7 0 1 1 0 14 7 7 0 0 1 0-14ZM5 12h14",
  storage: "m12 4 7 4v8l-7 4-7-4V8Z",
  settings: "M6 12h12M12 6v12M7.8 7.8l8.4 8.4M16.2 7.8l-8.4 8.4",
  personality: "M12 5 19 18H5Z",
  about: "M12 4v16M4 12h16",
  listen: "M12 6.5a3.5 3.5 0 0 1 3.5 3.5v2a3.5 3.5 0 0 1-7 0v-2A3.5 3.5 0 0 1 12 6.5Zm-5 5.5a5 5 0 0 0 10 0M12 17v3",
  quiet: "M7 7l10 10M17 7 7 17",
  clear: "M7 9h10M10 9V7.5a2 2 0 0 1 4 0V9m-5 3v4m4-4v4M8.5 9l.7 8.5a2 2 0 0 0 2 1.8h1.6a2 2 0 0 0 2-1.8L15.5 9",
  scan: "M5 12h4M15 12h4M12 5v4M12 15v4M8 8l2.5 2.5M13.5 13.5 16 16M8 16l2.5-2.5M13.5 10.5 16 8",
  load: "M12 5v10M8 11l4 4 4-4M5 19h14",
  switch: "M7 8h10l-2.5-2.5M17 16H7l2.5 2.5",
  release: "M6 16c2.2 1.8 4 2.5 6 2.5 3.8 0 6.5-2.3 7.5-6.2M18 8c-2.2-1.8-4-2.5-6-2.5C8.2 5.5 5.5 7.8 4.5 11.7",
  info: "M12 8v.1M12 11v5M12 3.5a8.5 8.5 0 1 1 0 17 8.5 8.5 0 0 1 0-17Z",
  language: "M5 12h14M12 5a11 11 0 0 1 0 14M12 5a11 11 0 0 0 0 14",
  motion: "M4 12h3l2-5 4 10 2-5h5",
  startup: "M12 4v10M8 10l4 4 4-4M5 19h14",
  memory: "M12 5.5 18 16H6Z",
  mood: "M12 6.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11Z",
  minimize: "M6 12h12",
  close: "M6 6l12 12M18 6 6 18",
  expand: "M8 4H4v4M16 4h4v4M4 16v4h4M20 16v4h-4",
  restore: "M7 7h10v10H7Z",
  breath: "M5 12c2.2-2.6 4.5-3.9 7-3.9s4.8 1.3 7 3.9c-2.2 2.6-4.5 3.9-7 3.9S7.2 14.6 5 12Z",
  stream: "M5 9c2 .8 4.4 1.2 7 1.2S17 9.8 19 9M5 15c2-.8 4.4-1.2 7-1.2S17 14.2 19 15",
  groupCore: "M12 4.8 18.2 16H5.8Z",
  groupRuntime: "m12 4.8 6.5 4.2v6l-6.5 4.2-6.5-4.2V9Z",
  groupInner: "M12 5.2a6.8 6.8 0 1 1 0 13.6 6.8 6.8 0 0 1 0-13.6Z"
};

export const SCENE_GROUPS = [
  { id: "core", title: "核心空间", titleEn: "Core", subtitle: "Home / Chat / Companion", iconPath: ICON_PATHS.groupCore },
  { id: "runtime", title: "运行空间", titleEn: "Runtime", subtitle: "Workbench / Loading / Storage", iconPath: ICON_PATHS.groupRuntime },
  { id: "inner", title: "内在空间", titleEn: "Inner", subtitle: "Settings / Personality / About", iconPath: ICON_PATHS.groupInner }
];

export const SCENES = [
  {
    id: "home",
    group: 0,
    title: "首页",
    titleEn: "Home Space",
    subtitle: "Lumi 正在静静地迎候你",
    iconPath: ICON_PATHS.home,
    background: background2,
    component: HomeScene
  },
  {
    id: "chat",
    group: 0,
    title: "对话空间",
    titleEn: "Chat Space",
    subtitle: "输入、倾听与回应在同一片空间里低声流动",
    iconPath: ICON_PATHS.chat,
    background: background3,
    component: ChatScene
  },
  {
    id: "companion",
    group: 0,
    title: "陪伴空间",
    titleEn: "Companion Space",
    subtitle: "让存在感、情绪与陪伴工具安静地停靠在人物之外",
    iconPath: ICON_PATHS.companion,
    background: background4,
    component: CompanionScene
  },
  {
    id: "workbench",
    group: 1,
    title: "工作台",
    titleEn: "Workbench",
    subtitle: "模型节点、状态与唤醒路径在这里被组织成有秩序的结构",
    iconPath: ICON_PATHS.workbench,
    background: background1,
    component: WorkbenchScene
  },
  {
    id: "loading",
    group: 1,
    title: "加载空间",
    titleEn: "Loading Space",
    subtitle: "把核心苏醒过程作为一段可感知的空间反馈来呈现",
    iconPath: ICON_PATHS.loading,
    background: background1,
    component: LoadingScene
  },
  {
    id: "storage",
    group: 1,
    title: "存储",
    titleEn: "Storage",
    subtitle: "在安静的视野里整理容量、缓存与本地资源的关系",
    iconPath: ICON_PATHS.storage,
    background: background1,
    component: StorageScene
  },
  {
    id: "settings",
    group: 2,
    title: "设置",
    titleEn: "Settings",
    subtitle: "把语言、动效与启动习惯收束为克制的系统控制",
    iconPath: ICON_PATHS.settings,
    background: background3,
    component: SettingsScene
  },
  {
    id: "personality",
    group: 2,
    title: "个性化",
    titleEn: "Personality",
    subtitle: "整理 Lumi 的回应倾向、呼吸节律与存在密度",
    iconPath: ICON_PATHS.personality,
    background: background3,
    component: PersonalityScene
  },
  {
    id: "about",
    group: 2,
    title: "关于 Lumi",
    titleEn: "About Lumi",
    subtitle: "回看当前版本、运行环境与这片空间的起点",
    iconPath: ICON_PATHS.about,
    background: background1,
    component: AboutScene
  }
];

export function getSceneById(sceneId) {
  return SCENES.find((scene) => scene.id === sceneId) || SCENES[0];
}

export function getSceneBackground(sceneId) {
  return getSceneById(sceneId).background || background2;
}
