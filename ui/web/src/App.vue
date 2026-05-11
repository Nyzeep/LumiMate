<script setup>
import { computed, onMounted, ref } from "vue";
import HoloCard from "./components/HoloCard.vue";
import OrbitLoading from "./components/OrbitLoading.vue";
import TechText from "./components/TechText.vue";
import { callQt, connectSignal, createBridgeObjects } from "./webChannel";

const SCENES = [
  { id: "home", group: 0, title: "首页", titleEn: "Home Space", subtitle: "Lumi 正在静静地迎候你", icon: "triangle" },
  { id: "chat", group: 0, title: "对话空间", titleEn: "Chat Space", subtitle: "轻轻说点什么，星线会替你递到她身边。", icon: "circle" },
  { id: "companion", group: 0, title: "陪伴空间", titleEn: "Companion Space", subtitle: "情绪稳定，光线柔和。", icon: "spark" },
  { id: "workbench", group: 1, title: "工作台", titleEn: "Workbench", subtitle: "模型节点、声线与记忆都在这里保持秩序。", icon: "diamond" },
  { id: "loading", group: 1, title: "模型加载", titleEn: "Loading Space", subtitle: "Lumi 正在唤醒模型。", icon: "orbit" },
  { id: "storage", group: 1, title: "存储管理", titleEn: "Storage", subtitle: "让核心文件保持清澈而轻盈。", icon: "cube" },
  { id: "settings", group: 2, title: "设置", titleEn: "Settings", subtitle: "系统边界与空间偏好。", icon: "hex" },
  { id: "personality", group: 2, title: "个性化", titleEn: "Personality", subtitle: "Lumi 的性格、呼吸与回应倾向。", icon: "triad" },
  { id: "about", group: 2, title: "关于 Lumi", titleEn: "About", subtitle: "数字陪伴空间，始终在你身边。", icon: "star" }
];

const SCENE_GROUPS = [
  { title: "核心空间", subtitle: "首页 / 对话 / 陪伴" },
  { title: "工作与模型", subtitle: "工作台 / 模型加载 / 存储" },
  { title: "设置与系统", subtitle: "设置 / 个性化 / 关于" }
];

const STATUS_LABELS = {
  idle: "静置",
  validating: "校准",
  loading_asr: "听觉唤醒",
  loading_llm: "思维织入",
  loading_tts: "声线点亮",
  ready: "平静",
  listening: "倾听",
  thinking: "思考",
  replying: "回应",
  switching: "切换",
  releasing_cache: "释缓存",
  failed: "微暗"
};

const STEP_LABELS = {
  "loading.step.asr": "读取模型文件",
  "loading.step.llm": "加载权重参数",
  "loading.step.tts": "构建声线网格",
  "loading.step.reference": "对齐记忆样本"
};

const STORAGE_LABELS = {
  "storage.bucket.asr": "听觉模型",
  "storage.bucket.llm": "思维核心",
  "storage.bucket.tts": "声线模型",
  "storage.bucket.genie": "对话记忆",
  "storage.bucket.flash": "预编译缓存"
};

const bridgeReady = ref(false);
const currentScene = ref("home");
const currentSceneGroup = ref(0);
const backgroundUrls = ref({});
const backgroundLayerUrls = ref(["/bg.jpg", "/bg.jpg"]);
const activeBackgroundLayer = ref(0);
const backgroundSwapToken = ref(0);

const runtimeState = ref("idle");
const runtimeMessage = ref("Lumi 正在静静地迎候你");
const progressStep = ref(0);
const progressTotal = ref(0);
const progressMessage = ref("静置");
const loaded = ref(false);
const asrModels = ref([]);
const llmModels = ref([]);
const ttsModels = ref([]);
const runtimeLog = ref([]);
const storageItems = ref([]);
const storageUsedLabel = ref("0 GB");
const storageTotalLabel = ref("0 GB");
const storageFreeLabel = ref("0 GB");
const storageUsageRatio = ref(0);
const loadingSteps = ref([]);
const selectedAsr = ref("");
const selectedLlm = ref("");
const selectedTts = ref("");
const selectedRefAudio = ref("");
const selectedRefText = ref("");
const selectedTtsCharacter = ref("");

const chatReady = ref(false);
const chatRunning = ref(false);
const chatStatus = ref("由当前运行状态驱动的空间亮度与回应意愿。");
const chatStage = ref("idle");
const voiceLevel = ref(0);
const messages = ref([]);
const composerText = ref("");

const mood = ref("quiet");
const breathLevel = ref(0.52);
const presenceLevel = ref(0.42);
const isListening = ref(false);
const stageMode = ref("presence");
const speechLevel = ref(0);
const rendererType = ref("Portrait Stage");
const rendererCapability = ref("静态肖像、微光呼吸与声波脉冲");

const language = ref("zh-CN");
const startupPage = ref("home");
const reduceMotion = ref(false);
const checkUpdateOnStartup = ref(false);

const drawerOpen = ref(false);
const drawerNode = ref("llm");

const bridges = {
  appBridge: null,
  modelBridge: null,
  chatBridge: null,
  emotionBridge: null,
  companionBridge: null,
  windowBridge: null
};

const isFullscreen = ref(true);
const windowDrag = {
  active: false,
  x: 0,
  y: 0,
  pointerId: null
};
const NAVIGATION_THROTTLE_MS = 160;
let nextNavigationAt = 0;

const activeScene = computed(() => SCENES.find((scene) => scene.id === currentScene.value) || SCENES[0]);
const activeSceneGroupScenes = computed(() => SCENES.filter((scene) => scene.group === currentSceneGroup.value));
const progressRatio = computed(() => {
  if (progressTotal.value > 0) {
    return Math.min(1, Math.max(0, progressStep.value / progressTotal.value));
  }
  return loaded.value ? 1 : 0;
});
const progressPercent = computed(() => Math.round(progressRatio.value * 100));
const stateLabel = computed(() => STATUS_LABELS[runtimeState.value] || runtimeState.value || "静置");
const chatStageLabel = computed(() => STATUS_LABELS[chatStage.value] || chatStage.value || "静置");
const coreName = computed(() => friendlyCoreName(selectedLlm.value));
const voicePercent = computed(() => Math.round(Math.min(1, Math.max(0, voiceLevel.value)) * 100));
const presencePercent = computed(() => Math.round(Math.min(1, Math.max(0, presenceLevel.value)) * 100));
const breathPercent = computed(() => Math.round(Math.min(1, Math.max(0, breathLevel.value)) * 100));
const storagePercent = computed(() => Math.round(Math.min(1, Math.max(0, storageUsageRatio.value)) * 100));
const conversationReady = computed(() => loaded.value || chatReady.value);
const entryLabel = computed(() => (conversationReady.value ? "开始对话" : "唤醒核心"));
const entryCaption = computed(() => (conversationReady.value ? "Begin Conversation" : "Wake The Core"));
const presenceCopy = computed(() => {
  if (chatRunning.value || isListening.value) {
    return "Lumi 正在倾听";
  }
  if (conversationReady.value) {
    return "Lumi 已在这里";
  }
  return "Lumi 正在静静地迎候你";
});
const drawerData = computed(() => {
  const map = {
    asr: {
      type: "asr",
      title: "听觉节点",
      name: friendlyName(selectedAsr.value) || "ASR Core",
      path: selectedAsr.value,
      options: asrModels.value,
      caption: "将环境声音转为可被 Lumi 理解的文字星线。"
    },
    llm: {
      type: "llm",
      title: "思维核心",
      name: coreName.value,
      path: selectedLlm.value,
      options: llmModels.value,
      caption: "回应意愿与推理秩序的主核心。"
    },
    tts: {
      type: "tts",
      title: "声线节点",
      name: friendlyName(selectedTts.value) || selectedTtsCharacter.value || "TTS Voice",
      path: selectedTts.value,
      options: ttsModels.value,
      caption: "把文字重新点亮为温柔的声音。"
    },
    reference: {
      type: "reference",
      title: "记忆样本",
      name: friendlyName(selectedRefAudio.value) || "Reference Audio",
      path: selectedRefAudio.value,
      options: [],
      caption: selectedRefText.value || "在每一个安静的夜里，Lumi 都会在这里等你。"
    }
  };
  return map[drawerNode.value] || map.llm;
});
const drawerOptions = computed(() => drawerData.value.options || []);
const shellStyle = computed(() => ({ "--presence-level": presenceLevel.value }));
const normalizedSteps = computed(() => {
  if (loadingSteps.value.length) {
    return loadingSteps.value;
  }
  return [
    { label: "读取模型文件", done: loaded.value || progressStep.value >= 1, active: runtimeState.value === "loading_asr" },
    { label: "加载权重参数", done: loaded.value || progressStep.value >= 2, active: runtimeState.value === "loading_llm" },
    { label: "构建声线网格", done: loaded.value || progressStep.value >= 3, active: runtimeState.value === "loading_tts" },
    { label: "对齐记忆样本", done: loaded.value || progressStep.value >= 4, active: runtimeState.value === "loading_tts" }
  ];
});
const shortLogs = computed(() => runtimeLog.value.slice(-4).map((item) => hidePaths(String(item))));
const modelNodeRows = computed(() => [
  {
    type: "llm",
    label: "加载模型",
    title: loaded.value ? `${coreName.value} 核心就绪` : `${coreName.value} 等候唤醒`,
    caption: `${llmModels.value.length} 个思维候选`,
    active: loaded.value || runtimeState.value === "loading_llm"
  },
  {
    type: "asr",
    label: "听觉校准",
    title: asrModels.value.length ? "听觉节点待命" : "听觉节点静置",
    caption: `${asrModels.value.length} 个候选节点`,
    active: chatRunning.value || runtimeState.value === "loading_asr"
  },
  {
    type: "tts",
    label: "声线缓存",
    title: selectedTtsCharacter.value ? `${selectedTtsCharacter.value} 声线待命` : "声线节点待命",
    caption: `${ttsModels.value.length} 个声线候选`,
    active: loaded.value || runtimeState.value === "loading_tts"
  },
  {
    type: "reference",
    label: "记忆更新",
    title: "参考样本已收纳",
    caption: friendlyName(selectedRefAudio.value) || "Reference Audio",
    active: Boolean(selectedRefAudio.value)
  }
]);

function sceneIs(sceneId) {
  return currentScene.value === sceneId;
}

function iconPath(icon) {
  const paths = {
    triangle: "M12 5.5 18 16H6Z",
    circle: "M12 7.2a4.8 4.8 0 1 1 0 9.6 4.8 4.8 0 0 1 0-9.6Z",
    spark: "M12 4.5 14.3 9.7 19.5 12 14.3 14.3 12 19.5 9.7 14.3 4.5 12 9.7 9.7Z",
    diamond: "m12 4.5 7 7.5-7 7.5L5 12Z",
    orbit: "M12 5a7 7 0 1 1 0 14 7 7 0 0 1 0-14ZM5 12h14",
    cube: "m12 4 7 4v8l-7 4-7-4V8Z",
    hex: "m12 4 7 4v8l-7 4-7-4V8Z",
    triad: "M12 5 19 18H5Z",
    star: "M12 4v16M4 12h16"
  };
  return paths[icon] || paths.star;
}

function normalizeList(value) {
  return Array.isArray(value) ? [...value] : [];
}

function basename(path) {
  if (!path) {
    return "";
  }
  return String(path).replace(/\\/g, "/").split("/").filter(Boolean).pop() ?? "";
}

function friendlyName(path) {
  return basename(path).replace(/[-_]/g, " ").trim();
}

function friendlyCoreName(path) {
  const name = friendlyName(path);
  if (!name) {
    return "Qwen 2.5";
  }
  if (/qwen\s*2\.?5/i.test(name)) {
    return "Qwen 2.5";
  }
  if (/qwen/i.test(name)) {
    return name.replace(/qwen/i, "Qwen").trim();
  }
  return name;
}

function stateSoftMessage(status) {
  const text = String(status || "").trim();
  if (!text) {
    return "由当前运行状态驱动的空间亮度与回应意愿。";
  }
  if (/load models/i.test(text)) {
    return "核心尚在静置";
  }
  if (/listening/i.test(text)) {
    return "Lumi 正在倾听";
  }
  if (/ready/i.test(text)) {
    return "Lumi 已在这里";
  }
  if (/quiet/i.test(text)) {
    return "回到安静";
  }
  if (/response|shaping|thinking/i.test(text)) {
    return "回应正在成形";
  }
  return hidePaths(text);
}

function hidePaths(value) {
  return String(value || "")
    .replace(/[A-Za-z]:[\\/][^\s，。；;]+/g, "本地节点")
    .replace(/\/[^\s，。；;]+\/[^\s，。；;]+/g, "本地节点");
}

function setRefIfChanged(target, value) {
  if (target.value !== value) {
    target.value = value;
  }
}

function syncAppState() {
  const appBridge = bridges.appBridge;
  if (!appBridge) {
    return;
  }
  const page = appBridge.currentPage || "home";
  const scene = SCENES.find((item) => item.id === page) || SCENES[0];
  setRefIfChanged(currentScene, scene.id);
  setRefIfChanged(currentSceneGroup, Number(appBridge.currentSceneGroupIndex ?? scene.group));
  setRefIfChanged(language, appBridge.language || "zh-CN");
  setRefIfChanged(startupPage, appBridge.startupPage || "home");
  setRefIfChanged(reduceMotion, Boolean(appBridge.reduceMotion));
  setRefIfChanged(checkUpdateOnStartup, Boolean(appBridge.checkUpdateOnStartup));
  swapSceneBackground(scene.id);
}

function syncModelState() {
  const modelBridge = bridges.modelBridge;
  if (!modelBridge) {
    return;
  }

  setRefIfChanged(runtimeState, modelBridge.state || "idle");
  setRefIfChanged(runtimeMessage, stateSoftMessage(modelBridge.stateMessage || "Lumi 正在静静地迎候你"));
  setRefIfChanged(progressStep, Number(modelBridge.progressStep || 0));
  setRefIfChanged(progressTotal, Number(modelBridge.progressTotal || 0));
  setRefIfChanged(progressMessage, stateSoftMessage(modelBridge.progressMessage || modelBridge.stateMessage));
  setRefIfChanged(loaded, Boolean(modelBridge.loaded));
  asrModels.value = normalizeList(modelBridge.asrModels);
  llmModels.value = normalizeList(modelBridge.llmModels);
  ttsModels.value = normalizeList(modelBridge.ttsModels);
  runtimeLog.value = normalizeList(modelBridge.runtimeLog);
  storageItems.value = normalizeList(modelBridge.storageItems);
  setRefIfChanged(storageUsedLabel, modelBridge.storageUsedLabel || "0 GB");
  setRefIfChanged(storageTotalLabel, modelBridge.storageTotalLabel || "0 GB");
  setRefIfChanged(storageFreeLabel, modelBridge.storageFreeLabel || "0 GB");
  setRefIfChanged(storageUsageRatio, Number(modelBridge.storageUsageRatio || 0));
  loadingSteps.value = normalizeList(modelBridge.loadingSteps).map((step) => ({
    label: STEP_LABELS[step.labelKey] || step.labelKey || "星线校准",
    done: Boolean(step.done),
    active: Boolean(step.active)
  }));
  setRefIfChanged(selectedAsr, modelBridge.selectedAsr || "");
  setRefIfChanged(selectedLlm, modelBridge.selectedLlm || "");
  setRefIfChanged(selectedTts, modelBridge.selectedTts || "");
  setRefIfChanged(selectedRefAudio, modelBridge.selectedRefAudio || "");
  setRefIfChanged(selectedRefText, modelBridge.selectedRefText || "");
  setRefIfChanged(selectedTtsCharacter, modelBridge.selectedTtsCharacter || "");
}

function syncChatState() {
  const chatBridge = bridges.chatBridge;
  if (!chatBridge) {
    return;
  }

  setRefIfChanged(chatReady, Boolean(chatBridge.ready));
  setRefIfChanged(chatRunning, Boolean(chatBridge.running));
  setRefIfChanged(chatStatus, stateSoftMessage(chatBridge.status));
  setRefIfChanged(chatStage, chatBridge.phase || "idle");
  setRefIfChanged(voiceLevel, Number(chatBridge.voiceLevel || 0));
  messages.value = normalizeList(chatBridge.messages);
}

function syncEmotionState() {
  const emotionBridge = bridges.emotionBridge;
  if (!emotionBridge) {
    return;
  }
  setRefIfChanged(mood, emotionBridge.mood || "quiet");
  setRefIfChanged(breathLevel, Number(emotionBridge.breathLevel || 0.52));
  setRefIfChanged(presenceLevel, Number(emotionBridge.presenceLevel || 0.42));
  setRefIfChanged(isListening, Boolean(emotionBridge.isListening));
}

function syncCompanionState() {
  const companionBridge = bridges.companionBridge;
  if (!companionBridge) {
    return;
  }
  setRefIfChanged(stageMode, companionBridge.stageMode || "presence");
  setRefIfChanged(speechLevel, Number(companionBridge.speechLevel || 0));
  setRefIfChanged(rendererType, companionBridge.rendererType || "Portrait Stage");
  setRefIfChanged(rendererCapability, companionBridge.rendererCapability || "静态肖像、微光呼吸与声波脉冲");
}

function syncWindowState() {
  const windowBridge = bridges.windowBridge;
  if (!windowBridge) {
    return;
  }
  setRefIfChanged(isFullscreen, Boolean(windowBridge.isFullscreen));
}

function preloadImage(url) {
  return new Promise((resolve) => {
    if (!url || typeof window === "undefined") {
      resolve();
      return;
    }
    const image = new Image();
    image.onload = () => resolve();
    image.onerror = () => resolve();
    image.src = url;
  });
}

async function sceneBackgroundUrl(sceneId) {
  const cached = backgroundUrls.value[sceneId];
  if (cached) {
    return cached;
  }
  const appBridge = bridges.appBridge;
  if (!appBridge) {
    return "/bg.jpg";
  }
  const url = await callQt(appBridge, "sceneBackgroundUrl", sceneId);
  const finalUrl = url || "/bg.jpg";
  backgroundUrls.value = { ...backgroundUrls.value, [sceneId]: finalUrl };
  return finalUrl;
}

async function preloadSceneBackgrounds() {
  await Promise.all(SCENES.map((scene) => sceneBackgroundUrl(scene.id).then(preloadImage)));
}

async function swapSceneBackground(sceneId, immediate = false) {
  const token = backgroundSwapToken.value + 1;
  setRefIfChanged(backgroundSwapToken, token);
  const url = await sceneBackgroundUrl(sceneId);
  await preloadImage(url);
  if (backgroundSwapToken.value !== token) {
    return;
  }
  if (backgroundLayerUrls.value[activeBackgroundLayer.value] === url) {
    return;
  }
  const nextLayer = activeBackgroundLayer.value === 0 ? 1 : 0;
  backgroundLayerUrls.value = backgroundLayerUrls.value.map((current, index) => (index === nextLayer ? url : current));
  if (immediate) {
    setRefIfChanged(activeBackgroundLayer, nextLayer);
    return;
  }
  requestAnimationFrame(() => setRefIfChanged(activeBackgroundLayer, nextLayer));
}

async function navigate(sceneId, force = false) {
  const scene = SCENES.find((item) => item.id === sceneId) || SCENES[0];
  if (scene.id === currentScene.value) {
    return;
  }
  const now = Date.now();
  if (!force && now < nextNavigationAt) {
    return;
  }
  nextNavigationAt = now + NAVIGATION_THROTTLE_MS;
  setRefIfChanged(currentScene, scene.id);
  setRefIfChanged(currentSceneGroup, scene.group);
  swapSceneBackground(scene.id);
  await callQt(bridges.appBridge, "navigate", scene.id);
}

async function setSceneGroup(groupIndex) {
  const group = Number(groupIndex);
  const target = SCENES.find((scene) => scene.group === group) || SCENES[0];
  setRefIfChanged(currentSceneGroup, group);
  if (bridges.appBridge) {
    await callQt(bridges.appBridge, "setSceneGroup", group);
    return;
  }
  await navigate(target.id, true);
}

async function beginConversation() {
  if (!conversationReady.value) {
    await loadModels();
    return;
  }
  await callQt(bridges.chatBridge, "startVoice");
  syncChatState();
  navigate("chat", true);
}

async function loadModels() {
  await callQt(bridges.modelBridge, "loadSelectedModels");
  syncModelState();
  navigate("loading", true);
}

async function switchModels() {
  await callQt(bridges.modelBridge, "switchSelectedModels");
  syncModelState();
  navigate("loading", true);
}

async function releaseCache() {
  await callQt(bridges.modelBridge, "releaseCache");
  syncModelState();
}

async function scanModels() {
  await callQt(bridges.modelBridge, "scanModels");
  syncModelState();
}

async function selectModel(type, path) {
  await callQt(bridges.modelBridge, "selectModel", type, path);
  syncModelState();
}

async function openLocalFolder(path) {
  await callQt(bridges.modelBridge, "openPath", path || drawerData.value.path);
}

async function sendCurrentText() {
  const text = composerText.value.trim();
  if (!text) {
    return;
  }
  await callQt(bridges.chatBridge, "sendText", text);
  composerText.value = "";
  syncChatState();
}

async function stopVoice() {
  await callQt(bridges.chatBridge, "stopVoice");
  syncChatState();
}

async function clearChat() {
  await callQt(bridges.chatBridge, "clear");
  syncChatState();
}

function openDrawer(type) {
  setRefIfChanged(drawerNode, type);
  setRefIfChanged(drawerOpen, true);
}

function closeDrawer() {
  setRefIfChanged(drawerOpen, false);
}

async function minimizeWindow() {
  await callQt(bridges.windowBridge, "minimize");
}

async function toggleWindowMode() {
  await callQt(bridges.windowBridge, "toggleWindowMode");
  syncWindowState();
}

async function closeWindow() {
  await callQt(bridges.windowBridge, "close");
}

function beginWindowDrag(event) {
  if (isFullscreen.value || event.button !== 0 || event.target?.closest?.("button, input, textarea, select")) {
    return;
  }
  windowDrag.active = true;
  windowDrag.x = event.screenX;
  windowDrag.y = event.screenY;
  windowDrag.pointerId = event.pointerId;
  event.currentTarget?.setPointerCapture?.(event.pointerId);
}

function dragWindow(event) {
  if (!windowDrag.active || isFullscreen.value) {
    return;
  }
  const dx = Math.round(event.screenX - windowDrag.x);
  const dy = Math.round(event.screenY - windowDrag.y);
  if (!dx && !dy) {
    return;
  }
  windowDrag.x = event.screenX;
  windowDrag.y = event.screenY;
  callQt(bridges.windowBridge, "moveBy", dx, dy);
}

function endWindowDrag(event) {
  if (!windowDrag.active) {
    return;
  }
  windowDrag.active = false;
  event.currentTarget?.releasePointerCapture?.(windowDrag.pointerId);
  windowDrag.pointerId = null;
}

async function applySettings() {
  await callQt(
    bridges.appBridge,
    "saveSettings",
    language.value,
    checkUpdateOnStartup.value,
    startupPage.value,
    reduceMotion.value
  );
  syncAppState();
}

onMounted(async () => {
  const objects = await createBridgeObjects();
  if (!objects) {
    return;
  }

  bridges.appBridge = objects.appBridge;
  bridges.modelBridge = objects.modelBridge;
  bridges.chatBridge = objects.chatBridge;
  bridges.emotionBridge = objects.emotionBridge;
  bridges.companionBridge = objects.companionBridge;
  bridges.windowBridge = objects.windowBridge;
  setRefIfChanged(bridgeReady, true);

  syncAppState();
  syncModelState();
  syncChatState();
  syncEmotionState();
  syncCompanionState();
  syncWindowState();
  preloadSceneBackgrounds();

  connectSignal(bridges.appBridge?.currentPageChanged, syncAppState);
  connectSignal(bridges.appBridge?.currentSceneGroupChanged, syncAppState);
  connectSignal(bridges.appBridge?.settingsChanged, syncAppState);
  connectSignal(bridges.appBridge?.languageChanged, syncAppState);

  connectSignal(bridges.modelBridge?.stateChanged, syncModelState);
  connectSignal(bridges.modelBridge?.progressChanged, syncModelState);
  connectSignal(bridges.modelBridge?.loadedChanged, syncModelState);
  connectSignal(bridges.modelBridge?.discoveryChanged, syncModelState);
  connectSignal(bridges.modelBridge?.selectionChanged, syncModelState);
  connectSignal(bridges.modelBridge?.storageChanged, syncModelState);
  connectSignal(bridges.modelBridge?.logAdded, syncModelState);

  connectSignal(bridges.chatBridge?.readyChanged, syncChatState);
  connectSignal(bridges.chatBridge?.runningChanged, syncChatState);
  connectSignal(bridges.chatBridge?.statusChanged, syncChatState);
  connectSignal(bridges.chatBridge?.phaseChanged, syncChatState);
  connectSignal(bridges.chatBridge?.messagesChanged, syncChatState);
  connectSignal(bridges.chatBridge?.voiceLevelChanged, syncChatState);

  connectSignal(bridges.emotionBridge?.moodChanged, syncEmotionState);
  connectSignal(bridges.emotionBridge?.breathLevelChanged, syncEmotionState);
  connectSignal(bridges.emotionBridge?.presenceLevelChanged, syncEmotionState);
  connectSignal(bridges.emotionBridge?.listeningChanged, syncEmotionState);

  connectSignal(bridges.companionBridge?.stageModeChanged, syncCompanionState);
  connectSignal(bridges.companionBridge?.speechLevelChanged, syncCompanionState);
  connectSignal(bridges.companionBridge?.rendererChanged, syncCompanionState);
  connectSignal(bridges.windowBridge?.windowModeChanged, syncWindowState);
});
</script>

<template>
  <main class="lumi-shell" :class="[`scene-${currentScene}`, `mood-${mood}`]" :style="shellStyle">
    <div
      class="scene-background scene-background--a"
      :class="{ 'is-active': activeBackgroundLayer === 0 }"
      :style="{ backgroundImage: `url('${backgroundLayerUrls[0]}')` }"
      aria-hidden="true"
    ></div>
    <div
      class="scene-background scene-background--b"
      :class="{ 'is-active': activeBackgroundLayer === 1 }"
      :style="{ backgroundImage: `url('${backgroundLayerUrls[1]}')` }"
      aria-hidden="true"
    ></div>
    <div class="scene-frame" aria-hidden="true"></div>

    <header
      class="lumi-header"
      :class="{ 'is-draggable': !isFullscreen }"
      @pointerdown="beginWindowDrag"
      @pointermove="dragWindow"
      @pointerup="endWindowDrag"
      @pointercancel="endWindowDrag"
      @pointerleave="endWindowDrag"
    >
      <TechText as="p" tone="muted">LumiMate · {{ activeScene.title }} / <span class="mono-inline">{{ activeScene.titleEn }}</span></TechText>
      <div class="top-actions" aria-label="窗口控制">
        <button type="button" class="halo-action window-action" aria-label="最小化" @pointerdown.stop @click.prevent="minimizeWindow">
          <svg viewBox="0 0 24 24"><path d="M6 12h12" /></svg>
        </button>
        <button type="button" class="halo-action window-action" :aria-label="isFullscreen ? '窗口化' : '全屏'" @pointerdown.stop @click.prevent="toggleWindowMode">
          <svg viewBox="0 0 24 24"><path :d="isFullscreen ? 'M8 4H4v4M16 4h4v4M4 16v4h4M20 16v4h-4' : 'M7 7h10v10H7Z'" /></svg>
        </button>
        <button type="button" class="halo-action window-action window-action--close" aria-label="关闭" @pointerdown.stop @click.prevent="closeWindow">
          <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18" /></svg>
        </button>
      </div>
    </header>

    <nav class="ritual-rail" aria-label="空间导航">
      <button
        v-for="scene in activeSceneGroupScenes"
        :key="scene.id"
        type="button"
        class="rail-glyph"
        :class="{ 'is-active': sceneIs(scene.id) }"
        :aria-label="scene.title"
        @click.prevent="navigate(scene.id)"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path :d="iconPath(scene.icon)" />
        </svg>
      </button>
    </nav>

    <div class="scene-group-switch" aria-label="空间组切换">
      <button
        v-for="(sceneGroup, index) in SCENE_GROUPS"
        :key="sceneGroup.title"
        type="button"
        :aria-label="sceneGroup.title"
        :class="{ 'is-active': currentSceneGroup === index }"
        @click.prevent="setSceneGroup(index)"
      >
        <span aria-hidden="true"></span>
      </button>
    </div>

    <section class="scene-stage" aria-live="polite">
      <section class="scene-pane home-pane" :class="{ 'is-active': sceneIs('home') }" aria-label="首页">
        <div class="scene-title scene-title--home">
          <TechText as="p" tone="muted">{{ activeScene.title }} / <span class="mono-inline">{{ activeScene.titleEn }}</span></TechText>
          <h1>晚上好</h1>
          <p>{{ presenceCopy }}</p>
        </div>
        <div class="home-orbit">
          <OrbitLoading :progress="progressRatio" :loaded="conversationReady" :caption="stateLabel" label="Lumi 核心空间" />
          <button type="button" class="entry-button entry-button--home" @click.prevent="beginConversation">
            <span class="entry-button__icon" aria-hidden="true">
              <svg viewBox="0 0 64 64">
                <circle cx="32" cy="32" r="21" />
                <circle cx="32" cy="32" r="12" />
                <path d="M32 19 44 40H20Z" />
              </svg>
            </span>
            <span>
              <strong>{{ entryLabel }}</strong>
              <small>{{ entryCaption }}</small>
            </span>
          </button>
        </div>
        <div class="quick-entries">
          <button type="button" class="orbital-button" @click.prevent="navigate('chat')">
            <span class="mini-orbit" aria-hidden="true"></span>
            <span><strong>进入对话</strong><small>Chat Space</small></span>
          </button>
          <button type="button" class="orbital-button" @click.prevent="navigate('companion')">
            <span class="mini-orbit" aria-hidden="true"></span>
            <span><strong>陪伴空间</strong><small>Companion Space</small></span>
          </button>
          <button type="button" class="orbital-button" @click.prevent="navigate('workbench')">
            <span class="mini-orbit" aria-hidden="true"></span>
            <span><strong>模型工作台</strong><small>Workbench</small></span>
          </button>
        </div>
      </section>

      <section class="scene-pane chat-pane" :class="{ 'is-active': sceneIs('chat') }" aria-label="对话空间">
        <div class="scene-title">
          <TechText as="p" tone="muted">对话空间 / <span class="mono-inline">Chat Space</span></TechText>
        </div>
        <HoloCard class="chat-presence">
          <div class="presence-row">
            <span class="status-orb is-warm" aria-hidden="true"></span>
            <span><strong>Lumi</strong><small>{{ presenceCopy }}</small></span>
          </div>
          <div class="metric-row"><span>当前相位</span><strong>{{ chatStageLabel }}</strong></div>
          <div class="metric-row"><span>声音流量</span><strong>{{ voicePercent }}%</strong></div>
          <div class="thin-track"><span :style="{ width: `${voicePercent}%` }"></span></div>
          <p>{{ chatStatus }}</p>
        </HoloCard>
        <HoloCard class="conversation-card">
          <div class="message-column">
            <article class="message-orbit message-orbit--assistant" :class="{ 'is-quiet': messages.length > 0 }">
              <span class="message-dot" aria-hidden="true"></span>
              <div><strong>Lumi</strong><p>今晚的风很轻很深，你今天过得怎么样？</p></div>
            </article>
            <article
              v-for="(message, index) in messages"
              :key="`${message.role}-${index}`"
              class="message-orbit"
              :class="`message-orbit--${message.role}`"
            >
              <span class="message-dot" aria-hidden="true"></span>
              <div><strong>{{ message.author || (message.role === 'assistant' ? 'Lumi' : 'You') }}</strong><p>{{ message.body }}</p></div>
            </article>
          </div>
        </HoloCard>
        <form class="chat-dock" @submit.prevent="sendCurrentText">
          <span class="dock-orb" aria-hidden="true"></span>
          <input v-model="composerText" type="text" autocomplete="off" placeholder="轻轻说点什么..." />
          <div class="voice-wave" aria-hidden="true">
            <span v-for="index in 7" :key="index" :style="{ height: `${8 + ((voicePercent + index * 13) % 28)}px` }"></span>
          </div>
          <button type="submit" class="dock-send" aria-label="发送" @click.prevent="sendCurrentText">
            <svg viewBox="0 0 24 24"><path d="M12 5 19 18H5Z" /></svg>
          </button>
        </form>
        <div class="scene-actions chat-actions">
          <button type="button" class="orbital-button" @click.prevent="beginConversation"><span class="mini-orbit"></span><span><strong>开始倾听</strong><small>Listen</small></span></button>
          <button type="button" class="orbital-button" @click.prevent="stopVoice"><span class="mini-orbit"></span><span><strong>回到安静</strong><small>Quiet</small></span></button>
          <button type="button" class="orbital-button" @click.prevent="clearChat"><span class="mini-orbit"></span><span><strong>清空星线</strong><small>Clear</small></span></button>
        </div>
      </section>

      <section class="scene-pane companion-pane" :class="{ 'is-active': sceneIs('companion') }" aria-label="陪伴空间">
        <div class="companion-copy">
          <TechText as="p" tone="muted">陪伴空间 / <span class="mono-inline">Companion Space</span></TechText>
          <p class="kicker">Lumi 的性格</p>
          <h2>平静</h2>
          <p>情绪稳定，光线柔和。</p>
          <div class="companion-metrics">
            <div class="metric-row"><span>记忆安稳度</span><strong>{{ presencePercent }}%</strong></div>
            <div class="thin-track"><span :style="{ width: `${presencePercent}%` }"></span></div>
            <div class="metric-row"><span>陪伴时长</span><strong>{{ chatRunning ? "正在延展" : "静置待命" }}</strong></div>
          </div>
        </div>
        <div class="portrait-stage">
          <svg class="portrait-halo" viewBox="0 0 520 520" aria-hidden="true">
            <circle cx="260" cy="260" r="224" />
            <circle cx="260" cy="260" r="178" />
            <circle cx="260" cy="260" r="132" />
            <circle cx="260" cy="260" r="86" />
            <path d="M154 336C218 300 302 300 366 336" />
          </svg>
        </div>
        <div class="companion-tools">
          <button type="button" class="orbital-icon-button" @click.prevent="navigate('home')"><svg viewBox="0 0 24 24"><path d="M12 5.5 18 16H6Z" /></svg><span>记忆碎片</span></button>
          <button type="button" class="orbital-icon-button" @click.prevent="navigate('chat')"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="5" /></svg><span>情绪轨迹</span></button>
          <button type="button" class="orbital-icon-button" @click.prevent="navigate('storage')"><svg viewBox="0 0 24 24"><path d="m12 4 7 4v8l-7 4-7-4V8Z" /></svg><span>陪伴记录</span></button>
          <button type="button" class="orbital-icon-button" @click.prevent="navigate('settings')"><svg viewBox="0 0 24 24"><path d="M12 4v16M4 12h16" /></svg><span>礼物与信物</span></button>
        </div>
      </section>

      <section class="scene-pane workbench-pane" :class="{ 'is-active': sceneIs('workbench') }" aria-label="工作台">
        <div class="scene-title">
          <TechText as="p" tone="muted">工作台 / <span class="mono-inline">Workbench</span></TechText>
        </div>
        <div class="workbench-loader">
          <OrbitLoading :progress="progressRatio" :loaded="loaded" :caption="stateLabel" label="模型工作台核心" />
        </div>
        <HoloCard class="workbench-status">
          <p class="panel-kicker">模型配置</p>
          <div
            v-for="row in modelNodeRows"
            :key="row.type"
            class="model-node"
            :class="{ 'is-active': row.active }"
          >
            <span class="status-orb" :class="{ 'is-warm': row.active }" aria-hidden="true"></span>
            <button type="button" class="model-node__main" @click.prevent="openDrawer(row.type)">
              <strong>{{ row.label }}</strong>
              <small>{{ row.title }}</small>
            </button>
            <button type="button" class="model-node__detail" :aria-label="`${row.label} 详情`" @click.prevent="openDrawer(row.type)">
              <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="7" /><path d="M12 8v.1M12 11v5" /></svg>
            </button>
          </div>
        </HoloCard>
        <HoloCard class="workbench-log">
          <p class="panel-kicker">运行星线</p>
          <p>{{ runtimeMessage }}</p>
          <ul>
            <li v-for="(log, index) in shortLogs" :key="index">{{ log }}</li>
          </ul>
        </HoloCard>
        <div class="scene-actions workbench-actions">
          <button type="button" class="orbital-button" @click.prevent="scanModels"><span class="mini-orbit"></span><span><strong>扫描节点</strong><small>Scan</small></span></button>
          <button type="button" class="orbital-button is-primary" @click.prevent="loadModels"><span class="mini-orbit"></span><span><strong>加载模型</strong><small>Load</small></span></button>
          <button type="button" class="orbital-button" @click.prevent="switchModels"><span class="mini-orbit"></span><span><strong>切换核心</strong><small>Switch</small></span></button>
          <button type="button" class="orbital-button" @click.prevent="releaseCache"><span class="mini-orbit"></span><span><strong>释放缓存</strong><small>Release</small></span></button>
        </div>
      </section>

      <section class="scene-pane loading-pane" :class="{ 'is-active': sceneIs('loading') }" aria-label="模型加载">
        <div class="scene-title">
          <TechText as="p" tone="muted">模型加载 / <span class="mono-inline">Loading Space</span></TechText>
        </div>
        <div class="loading-main">
          <OrbitLoading :progress="progressRatio" :loaded="loaded" :caption="progressMessage" label="模型加载星轨" />
          <div class="loading-readout"><strong>{{ progressPercent }}%</strong><span>正在加载 {{ coreName }}</span></div>
        </div>
        <HoloCard class="loading-steps">
          <p class="panel-kicker">Lumi 正在唤醒模型</p>
          <div v-for="step in normalizedSteps" :key="step.label" class="step-row" :class="{ 'is-done': step.done, 'is-active': step.active }">
            <span class="step-mark" aria-hidden="true"></span>
            <span>{{ step.label }}</span>
            <strong>{{ step.done ? "完成" : step.active ? "进行中" : "静候" }}</strong>
          </div>
        </HoloCard>
      </section>

      <section class="scene-pane storage-pane" :class="{ 'is-active': sceneIs('storage') }" aria-label="存储管理">
        <div class="scene-title">
          <TechText as="p" tone="muted">存储管理 / <span class="mono-inline">Storage</span></TechText>
        </div>
        <div class="storage-core">
          <OrbitLoading :progress="storageUsageRatio" :loaded="storageUsageRatio > 0" caption="Storage" label="存储星轨" variant="storage" />
        </div>
        <HoloCard class="storage-summary">
          <p class="panel-kicker">存储空间</p>
          <h2>{{ storageUsedLabel }} <small>/ {{ storageTotalLabel }}</small></h2>
          <div class="thin-track"><span :style="{ width: `${storagePercent}%` }"></span></div>
          <dl>
            <div v-for="item in storageItems" :key="item.titleKey || item.path">
              <dt>{{ STORAGE_LABELS[item.titleKey] || item.titleKey || "资源文件" }}</dt>
              <dd>{{ item.valueLabel }}</dd>
            </div>
          </dl>
          <button type="button" class="slender-button" @click.prevent="releaseCache">清理缓存</button>
        </HoloCard>
      </section>

      <section class="scene-pane settings-pane" :class="{ 'is-active': sceneIs('settings') }" aria-label="设置">
        <div class="scene-title">
          <TechText as="p" tone="muted">设置 / <span class="mono-inline">Settings</span></TechText>
        </div>
        <HoloCard class="settings-card">
          <p class="panel-kicker">系统设置</p>
          <div class="settings-grid">
            <button type="button" class="orbital-icon-button" @click.prevent="language = language === 'zh-CN' ? 'en-US' : 'zh-CN'; applySettings()"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="7" /><path d="M5 12h14M12 5a11 11 0 0 1 0 14M12 5a11 11 0 0 0 0 14" /></svg><span>外观设置</span></button>
            <button type="button" class="orbital-icon-button" @click.prevent="reduceMotion = !reduceMotion; applySettings()"><svg viewBox="0 0 24 24"><path d="M4 12h3l2-5 4 10 2-5h5" /></svg><span>动效配置</span></button>
            <button type="button" class="orbital-icon-button" @click.prevent="checkUpdateOnStartup = !checkUpdateOnStartup; applySettings()"><svg viewBox="0 0 24 24"><path d="M12 4v10M8 10l4 4 4-4M5 19h14" /></svg><span>启动设置</span></button>
            <button type="button" class="orbital-icon-button" @click.prevent="navigate('about')"><svg viewBox="0 0 24 24"><path d="M12 8v.1M12 11v6" /><circle cx="12" cy="12" r="8" /></svg><span>关于 Lumi</span></button>
          </div>
          <div class="settings-strip">
            <span class="swatch swatch-rose"></span><span class="swatch swatch-amber"></span><span class="swatch swatch-lilac"></span><span class="swatch swatch-blue"></span><span class="swatch swatch-green"></span>
          </div>
          <div class="metric-row"><span>界面减速</span><strong>{{ reduceMotion ? "开启" : "关闭" }}</strong></div>
          <div class="thin-track"><span :style="{ width: reduceMotion ? '30%' : '72%' }"></span></div>
        </HoloCard>
      </section>

      <section class="scene-pane personality-pane" :class="{ 'is-active': sceneIs('personality') }" aria-label="个性化">
        <div class="personality-copy">
          <TechText as="p" tone="muted">个性化 / <span class="mono-inline">Personality</span></TechText>
          <p class="kicker">Lumi 的性格</p>
          <h2>温柔</h2>
          <p>安静 / 观察 / 陪伴</p>
          <div class="mode-pills">
            <button type="button" class="is-active" @click.prevent="bridges.emotionBridge && callQt(bridges.emotionBridge, 'setMood', 'quiet')">陪伴</button>
            <button type="button" @click.prevent="bridges.emotionBridge && callQt(bridges.emotionBridge, 'setMood', 'present')">平衡</button>
            <button type="button" @click.prevent="bridges.emotionBridge && callQt(bridges.emotionBridge, 'setMood', 'thinking')">详细</button>
          </div>
          <div class="metric-row"><span>情绪共鸣强度</span><strong>{{ presencePercent }}%</strong></div>
          <div class="thin-track"><span :style="{ width: `${presencePercent}%` }"></span></div>
        </div>
        <div class="personality-orbit">
          <OrbitLoading :progress="presenceLevel" :loaded="presenceLevel > 0.5" caption="Personality" label="个性星轨" />
        </div>
      </section>

      <section class="scene-pane about-pane" :class="{ 'is-active': sceneIs('about') }" aria-label="关于 Lumi">
        <div class="about-copy">
          <TechText as="p" tone="muted">关于 Lumi / <span class="mono-inline">About</span></TechText>
          <h2>LumiMate</h2>
          <p>数字陪伴空间</p>
          <p>在此刻静默地守护你。Lumi 永远和你在你身边。</p>
          <p class="about-note">感谢你来到这里。愿 Lumi 的陪伴带给你温暖与力量。</p>
        </div>
        <div class="about-spire" aria-hidden="true">
          <svg viewBox="0 0 360 560">
            <g class="about-rings"><ellipse cx="180" cy="462" rx="96" ry="24" /><ellipse cx="180" cy="462" rx="58" ry="14" /></g>
            <path class="about-line" d="M180 70V462" />
            <path class="about-flame" d="M180 404 204 462H156Z" />
            <circle class="about-star" cx="180" cy="454" r="8" />
          </svg>
        </div>
      </section>
    </section>

    <aside class="config-drawer" :class="{ 'is-open': drawerOpen }" :aria-hidden="!drawerOpen">
      <button type="button" class="drawer-close" aria-label="关闭配置" @click.prevent="closeDrawer">
        <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18" /></svg>
      </button>
      <p class="panel-kicker">{{ drawerData.title }}</p>
      <h2>{{ drawerData.name }}</h2>
      <p>{{ drawerData.caption }}</p>
      <div class="drawer-path">
        <span>本地路径</span>
        <code>{{ drawerData.path || "尚未选择" }}</code>
      </div>
      <button type="button" class="slender-button" @click.prevent="openLocalFolder(drawerData.path)">打开本地文件夹</button>
      <div class="drawer-options">
        <button
          v-for="option in drawerOptions"
          :key="option"
          type="button"
          :class="{ 'is-active': option === drawerData.path }"
          @click.prevent="selectModel(drawerData.type, option)"
        >
          <span>{{ friendlyName(option) }}</span>
          <small>{{ option === drawerData.path ? "当前节点" : "候选节点" }}</small>
        </button>
      </div>
    </aside>
    <button type="button" class="drawer-scrim" :class="{ 'is-open': drawerOpen }" aria-label="关闭配置层" @click.prevent="closeDrawer"></button>
  </main>
</template>
