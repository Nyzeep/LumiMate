import { computed, reactive } from "vue";
import { callQt, connectSignal, createBridgeObjects } from "../webChannel";

const STATUS_LABELS = {
  idle: "\u9759\u7f6e",
  validating: "\u6821\u51c6",
  loading_asr: "\u542c\u89c9\u5524\u9192",
  loading_llm: "\u601d\u7ef4\u7ec7\u5165",
  loading_tts: "\u58f0\u7ebf\u70b9\u4eae",
  ready: "\u5e73\u9759",
  listening: "\u503e\u542c",
  thinking: "\u601d\u7d22",
  replying: "\u56de\u5e94",
  switching: "\u5207\u6362",
  releasing_cache: "\u91ca\u653e\u7f13\u5b58",
  checking_update: "\u68c0\u67e5\u66f4\u65b0",
  failed: "\u5fae\u6697"
};

const STEP_LABELS = {
  "loading.step.asr": "\u8bfb\u53d6\u542c\u89c9\u8282\u70b9",
  "loading.step.llm": "\u6821\u51c6\u601d\u7ef4\u6838\u5fc3",
  "loading.step.tts": "\u70b9\u4eae\u58f0\u7ebf\u7f51\u7edc",
  "loading.step.reference": "\u5bf9\u9f50\u8bb0\u5fc6\u6837\u672c"
};

const STORAGE_LABELS = {
  "storage.bucket.asr": "\u542c\u89c9\u6a21\u578b\u5c42",
  "storage.bucket.llm": "\u601d\u7ef4\u6838\u5fc3\u5c42",
  "storage.bucket.tts": "\u58f0\u7ebf\u6a21\u578b\u5c42",
  "storage.bucket.genie": "\u5bf9\u8bdd\u8bb0\u5fc6\u5c42",
  "storage.bucket.flash": "\u7f13\u5b58\u9884\u7f16\u8bd1\u5c42"
};

const BOOT_PHASE_COPY = {
  starting: "Gathering starlight",
  "page-loading": "Unfolding the first veil",
  "page-loaded": "Settling the background",
  "frontend-ready": "Waiting in quiet light",
  revealing: "Opening the space",
  revealed: "Ready",
  "load-failed": "Returning to stillness"
};

const MOOD_LABELS = {
  quiet: "\u9759\u7f6e",
  present: "\u5728\u573a",
  awakening: "\u82cf\u9192",
  listening: "\u503e\u542c",
  thinking: "\u601d\u7d22",
  replying: "\u56de\u5e94",
  dim: "\u5fae\u6697"
};

const AMBIENT_MODE_LABELS = {
  quiet: "\u9759\u8c27",
  breath: "\u547c\u5438",
  stream: "\u661f\u6d41"
};

function normalizeList(value) {
  return Array.isArray(value) ? [...value] : [];
}

function normalizeCatalog(value) {
  if (!value || typeof value !== "object") {
    return { asr: [], llm: [], tts: [], reference: [] };
  }

  const normalizeEntries = (entries) =>
    normalizeList(entries).map((entry) => ({
      id: entry.id || "",
      title: entry.title || "\u672a\u547d\u540d\u8282\u70b9",
      subtitle: entry.subtitle || "",
      tags: normalizeList(entry.tags),
      status: entry.status || "idle",
      selected: Boolean(entry.selected),
      kind: entry.kind || "",
      path: entry.path || ""
    }));

  return {
    asr: normalizeEntries(value.asr),
    llm: normalizeEntries(value.llm),
    tts: normalizeEntries(value.tts),
    reference: normalizeEntries(value.reference)
  };
}

function normalizeComponentStatus(value) {
  const fallback = {
    asr: { kind: "asr", label: "听觉节点", ready: false, count: 0, selected: "", selectedName: "", status: "missing", note: "等待下载或导入模型。" },
    llm: { kind: "llm", label: "思维核心", ready: false, count: 0, selected: "", selectedName: "", status: "missing", note: "等待下载或导入模型。" },
    tts: { kind: "tts", label: "声线节点", ready: false, count: 0, selected: "", selectedName: "", status: "placeholder", note: "TTS 远程下载暂未开放。" },
    ready: false,
    missingRequired: ["asr", "llm"]
  };
  if (!value || typeof value !== "object") {
    return fallback;
  }
  const normalizeNode = (kind) => ({
    ...fallback[kind],
    ...(value[kind] || {}),
    ready: Boolean(value[kind]?.ready),
    count: Number(value[kind]?.count || 0),
    selected: value[kind]?.selected || "",
    selectedName: value[kind]?.selectedName || "",
    status: value[kind]?.status || fallback[kind].status,
    note: value[kind]?.note || fallback[kind].note
  });
  return {
    asr: normalizeNode("asr"),
    llm: normalizeNode("llm"),
    tts: normalizeNode("tts"),
    ready: Boolean(value.ready),
    missingRequired: normalizeList(value.missingRequired)
  };
}

function normalizeDownloadCatalog(value) {
  const normalizeItem = (item) => ({
    id: item.id || item.title || "",
    title: item.title || "未命名模型",
    subtitle: item.subtitle || "",
    sizeLabel: item.sizeLabel || "",
    providers: item.providers && typeof item.providers === "object" ? { ...item.providers } : {},
    placeholder: Boolean(item.placeholder)
  });
  if (!value || typeof value !== "object") {
    return { asr: [], llm: [], tts: [] };
  }
  return {
    asr: normalizeList(value.asr).map(normalizeItem),
    llm: normalizeList(value.llm).map(normalizeItem),
    tts: normalizeList(value.tts).map(normalizeItem)
  };
}

function basename(path) {
  if (!path) {
    return "";
  }
  return String(path).replace(/\\/g, "/").split("/").filter(Boolean).pop() ?? "";
}

function hidePaths(value) {
  return String(value || "")
    .replace(/[A-Za-z]:[\\/][^\s,;:]+/g, "\u672c\u5730\u8282\u70b9")
    .replace(/\/[^\s,;:]+\/[^\s,;:]+/g, "\u672c\u5730\u8282\u70b9");
}

function setIfChanged(target, key, value) {
  if (target[key] !== value) {
    target[key] = value;
  }
}

function clamp01(value) {
  return Math.min(1, Math.max(0, Number(value) || 0));
}

function pickSelected(entries) {
  return entries.find((entry) => entry.selected) || entries[0] || null;
}

function normalizeMessages(items) {
  return normalizeList(items).map((item) => ({
    role: item.role || "assistant",
    author: item.author || (item.role === "user" ? "You" : "Lumi"),
    body: hidePaths(item.body || "")
  }));
}

function softMessage(status) {
  const text = hidePaths(status).trim();
  if (!text) {
    return "\u7531\u5f53\u524d\u8fd0\u884c\u72b6\u6001\u9a71\u52a8\u7684\u7a7a\u95f4\u4eae\u5ea6\u4e0e\u56de\u5e94\u610f\u613f\u3002";
  }
  if (/load models|wake lumi/i.test(text)) {
    return "\u6838\u5fc3\u4ecd\u5728\u9759\u7f6e\uff0c\u7b49\u5f85\u88ab\u5524\u9192\u3002";
  }
  if (/listening/i.test(text)) {
    return "Lumi \u6b63\u5728\u503e\u542c\u3002";
  }
  if (/ready/i.test(text)) {
    return "Lumi \u5df2\u7ecf\u5728\u8fd9\u91cc\u3002";
  }
  if (/quiet/i.test(text)) {
    return "\u7a7a\u95f4\u56de\u5230\u5b89\u9759\u3002";
  }
  if (/response|shaping|thinking/i.test(text)) {
    return "\u56de\u5e94\u6b63\u5728\u6210\u5f62\u3002";
  }
  return text;
}

export function useBridgeState() {
  const state = reactive({
    boot: {
      bridgeReady: false,
      phase: "starting",
      ready: false
    },
    app: {
      currentScene: "home",
      currentSceneGroup: 0,
      language: "zh-CN",
      startupPage: "home",
      reduceMotion: false,
      checkUpdateOnStartup: false,
      ambientMode: "quiet",
      appVersion: "",
      appAuthor: "",
      projectUrl: "",
      authorAvatarUrl: "",
      updateSource: "",
      projectRoot: "",
      pythonExecutable: ""
    },
    ui: {
      drawerOpen: false,
      drawerNode: "llm",
      composerText: ""
    },
    runtime: {
      state: "idle",
      message: "Lumi \u6b63\u5728\u9759\u9759\u5730\u8fce\u5019\u4f60",
      progressStep: 0,
      progressTotal: 0,
      progressMessage: "\u9759\u7f6e",
      loaded: false,
      logs: [],
      loadingSteps: [],
      modelCatalog: { asr: [], llm: [], tts: [], reference: [] },
      storageItems: [],
      storageUsedLabel: "0 GB",
      storageTotalLabel: "0 GB",
      storageFreeLabel: "0 GB",
      storageUsageRatio: 0,
      selectedAsr: "",
      selectedLlm: "",
      selectedTts: "",
      selectedRefAudio: "",
      selectedRefText: "",
      selectedTtsCharacter: "",
      componentStatus: normalizeComponentStatus(null),
      downloadCatalog: normalizeDownloadCatalog(null),
      downloadState: "idle",
      downloadProgress: 0,
      downloadMessage: "等待选择模型星系。",
      downloadLogs: []
    },
    chat: {
      ready: false,
      running: false,
      status: "\u7531\u5f53\u524d\u8fd0\u884c\u72b6\u6001\u9a71\u52a8\u7684\u7a7a\u95f4\u4eae\u5ea6\u4e0e\u56de\u5e94\u610f\u613f\u3002",
      phase: "idle",
      voiceLevel: 0,
      messages: []
    },
    emotion: {
      mood: "quiet",
      breathLevel: 0.52,
      presenceLevel: 0.42,
      isListening: false
    },
    companion: {
      stageMode: "presence",
      speechLevel: 0,
      rendererType: "Portrait Stage",
      rendererCapability: "\u9759\u6001\u8096\u50cf\u3001\u5fae\u5149\u547c\u5438\u4e0e\u58f0\u6ce2\u8109\u51b2"
    },
    window: {
      isFullscreen: true
    }
  });

  const bridges = reactive({
    appBridge: null,
    modelBridge: null,
    chatBridge: null,
    emotionBridge: null,
    companionBridge: null,
    shellBridge: null,
    windowBridge: null
  });

  const scheduledSyncs = new Map();
  let frameToken = 0;

  function scheduleSync(key, task) {
    scheduledSyncs.set(key, task);
    if (frameToken) {
      return;
    }
    frameToken = window.requestAnimationFrame(() => {
      const tasks = [...scheduledSyncs.values()];
      scheduledSyncs.clear();
      frameToken = 0;
      tasks.forEach((item) => item());
    });
  }

  function syncBootState() {
    if (state.boot.ready) {
      return;
    }
    setIfChanged(state.boot, "phase", bridges.shellBridge?.bootPhase || "starting");
    setIfChanged(state.boot, "ready", state.boot.phase === "revealed");
  }

  function syncAppState() {
    const appBridge = bridges.appBridge;
    if (!appBridge) {
      return;
    }
    setIfChanged(state.app, "currentScene", appBridge.currentPage || "home");
    setIfChanged(state.app, "currentSceneGroup", Number(appBridge.currentSceneGroupIndex ?? 0));
    setIfChanged(state.app, "language", appBridge.language || "zh-CN");
    setIfChanged(state.app, "startupPage", appBridge.startupPage || "home");
    setIfChanged(state.app, "reduceMotion", Boolean(appBridge.reduceMotion));
    setIfChanged(state.app, "checkUpdateOnStartup", Boolean(appBridge.checkUpdateOnStartup));
    setIfChanged(state.app, "ambientMode", appBridge.ambientMode || "quiet");
    setIfChanged(state.app, "appVersion", appBridge.appVersion || "");
    setIfChanged(state.app, "appAuthor", appBridge.appAuthor || "");
    setIfChanged(state.app, "projectUrl", appBridge.projectUrl || "");
    setIfChanged(state.app, "authorAvatarUrl", appBridge.authorAvatarUrl || "");
    setIfChanged(state.app, "updateSource", appBridge.updateSource || "");
    setIfChanged(state.app, "projectRoot", appBridge.projectRoot || "");
    setIfChanged(state.app, "pythonExecutable", appBridge.pythonExecutable || "");
  }

  function syncModelState() {
    const modelBridge = bridges.modelBridge;
    if (!modelBridge) {
      return;
    }

    setIfChanged(state.runtime, "state", modelBridge.state || "idle");
    setIfChanged(state.runtime, "message", softMessage(modelBridge.stateMessage || "Lumi \u6b63\u5728\u9759\u9759\u5730\u8fce\u5019\u4f60"));
    setIfChanged(state.runtime, "progressStep", Number(modelBridge.progressStep || 0));
    setIfChanged(state.runtime, "progressTotal", Number(modelBridge.progressTotal || 0));
    setIfChanged(state.runtime, "progressMessage", softMessage(modelBridge.progressMessage || modelBridge.stateMessage));
    setIfChanged(state.runtime, "loaded", Boolean(modelBridge.loaded));
    state.runtime.logs = normalizeList(modelBridge.runtimeLog).map((item) => hidePaths(item));
    state.runtime.loadingSteps = normalizeList(modelBridge.loadingSteps).map((step) => ({
      label: STEP_LABELS[step.labelKey] || step.labelKey || "\u661f\u7ebf\u6821\u51c6",
      done: Boolean(step.done),
      active: Boolean(step.active)
    }));
    state.runtime.modelCatalog = normalizeCatalog(modelBridge.modelCatalog);
    state.runtime.componentStatus = normalizeComponentStatus(modelBridge.componentStatus);
    state.runtime.downloadCatalog = normalizeDownloadCatalog(modelBridge.downloadCatalog);
    setIfChanged(state.runtime, "downloadState", modelBridge.downloadState || "idle");
    setIfChanged(state.runtime, "downloadProgress", Number(modelBridge.downloadProgress || 0));
    setIfChanged(state.runtime, "downloadMessage", hidePaths(modelBridge.downloadMessage || "等待选择模型星系。"));
    state.runtime.downloadLogs = normalizeList(modelBridge.downloadLogs).map((item) => hidePaths(item)).filter(Boolean);
    state.runtime.storageItems = normalizeList(modelBridge.storageItems).map((item) => ({
      label: STORAGE_LABELS[item.titleKey] || item.titleKey || "\u672c\u5730\u8d44\u6e90",
      valueLabel: item.valueLabel || "0 GB",
      titleKey: item.titleKey || "",
      path: item.path || ""
    }));

    setIfChanged(state.runtime, "storageUsedLabel", modelBridge.storageUsedLabel || "0 GB");
    setIfChanged(state.runtime, "storageTotalLabel", modelBridge.storageTotalLabel || "0 GB");
    setIfChanged(state.runtime, "storageFreeLabel", modelBridge.storageFreeLabel || "0 GB");
    setIfChanged(state.runtime, "storageUsageRatio", Number(modelBridge.storageUsageRatio || 0));
    setIfChanged(state.runtime, "selectedAsr", modelBridge.selectedAsr || "");
    setIfChanged(state.runtime, "selectedLlm", modelBridge.selectedLlm || "");
    setIfChanged(state.runtime, "selectedTts", modelBridge.selectedTts || "");
    setIfChanged(state.runtime, "selectedRefAudio", modelBridge.selectedRefAudio || "");
    setIfChanged(state.runtime, "selectedRefText", modelBridge.selectedRefText || "");
    setIfChanged(state.runtime, "selectedTtsCharacter", modelBridge.selectedTtsCharacter || "");
  }

  function syncChatState() {
    const chatBridge = bridges.chatBridge;
    if (!chatBridge) {
      return;
    }
    setIfChanged(state.chat, "ready", Boolean(chatBridge.ready));
    setIfChanged(state.chat, "running", Boolean(chatBridge.running));
    setIfChanged(state.chat, "status", softMessage(chatBridge.status));
    setIfChanged(state.chat, "phase", chatBridge.phase || "idle");
    setIfChanged(state.chat, "voiceLevel", clamp01(chatBridge.voiceLevel));
    state.chat.messages = normalizeMessages(chatBridge.messages);
  }

  function syncEmotionState() {
    const emotionBridge = bridges.emotionBridge;
    if (!emotionBridge) {
      return;
    }
    setIfChanged(state.emotion, "mood", emotionBridge.mood || "quiet");
    setIfChanged(state.emotion, "breathLevel", clamp01(emotionBridge.breathLevel || 0.52));
    setIfChanged(state.emotion, "presenceLevel", clamp01(emotionBridge.presenceLevel || 0.42));
    setIfChanged(state.emotion, "isListening", Boolean(emotionBridge.isListening));
  }

  function syncCompanionState() {
    const companionBridge = bridges.companionBridge;
    if (!companionBridge) {
      return;
    }
    setIfChanged(state.companion, "stageMode", companionBridge.stageMode || "presence");
    setIfChanged(state.companion, "speechLevel", clamp01(companionBridge.speechLevel || 0));
    setIfChanged(state.companion, "rendererType", companionBridge.rendererType || "Portrait Stage");
    setIfChanged(
      state.companion,
      "rendererCapability",
      companionBridge.rendererCapability || "\u9759\u6001\u8096\u50cf\u3001\u5fae\u5149\u547c\u5438\u4e0e\u58f0\u6ce2\u8109\u51b2"
    );
  }

  function syncWindowState() {
    const windowBridge = bridges.windowBridge;
    if (!windowBridge) {
      return;
    }
    setIfChanged(state.window, "isFullscreen", Boolean(windowBridge.isFullscreen));
  }

  function syncAll() {
    syncBootState();
    syncAppState();
    syncModelState();
    syncChatState();
    syncEmotionState();
    syncCompanionState();
    syncWindowState();
  }

  async function initBridges() {
    const objects = await createBridgeObjects();
    if (!objects) {
      return false;
    }

    Object.assign(bridges, {
      appBridge: objects.appBridge,
      modelBridge: objects.modelBridge,
      chatBridge: objects.chatBridge,
      emotionBridge: objects.emotionBridge,
      companionBridge: objects.companionBridge,
      shellBridge: objects.shellBridge,
      windowBridge: objects.windowBridge
    });

    state.boot.bridgeReady = true;
    syncAll();

    connectSignal(bridges.shellBridge?.bootPhaseChanged, () => scheduleSync("boot", syncBootState));

    connectSignal(bridges.appBridge?.currentPageChanged, () => scheduleSync("app", syncAppState));
    connectSignal(bridges.appBridge?.currentSceneGroupChanged, () => scheduleSync("app", syncAppState));
    connectSignal(bridges.appBridge?.settingsChanged, () => scheduleSync("app", syncAppState));
    connectSignal(bridges.appBridge?.languageChanged, () => scheduleSync("app", syncAppState));
    connectSignal(bridges.appBridge?.ambientModeChanged, () => scheduleSync("app", syncAppState));

    connectSignal(bridges.modelBridge?.stateChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.progressChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.loadedChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.discoveryChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.selectionChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.storageChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.logAdded, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.componentStatusChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.downloadCatalogChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.downloadStateChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.downloadProgressChanged, () => scheduleSync("model", syncModelState));
    connectSignal(bridges.modelBridge?.downloadLogAdded, () => scheduleSync("model", syncModelState));

    connectSignal(bridges.chatBridge?.readyChanged, () => scheduleSync("chat", syncChatState));
    connectSignal(bridges.chatBridge?.runningChanged, () => scheduleSync("chat", syncChatState));
    connectSignal(bridges.chatBridge?.statusChanged, () => scheduleSync("chat", syncChatState));
    connectSignal(bridges.chatBridge?.phaseChanged, () => scheduleSync("chat", syncChatState));
    connectSignal(bridges.chatBridge?.messagesChanged, () => scheduleSync("chat", syncChatState));
    connectSignal(bridges.chatBridge?.voiceLevelChanged, () => scheduleSync("chat", syncChatState));

    connectSignal(bridges.emotionBridge?.moodChanged, () => scheduleSync("emotion", syncEmotionState));
    connectSignal(bridges.emotionBridge?.breathLevelChanged, () => scheduleSync("emotion", syncEmotionState));
    connectSignal(bridges.emotionBridge?.presenceLevelChanged, () => scheduleSync("emotion", syncEmotionState));
    connectSignal(bridges.emotionBridge?.listeningChanged, () => scheduleSync("emotion", syncEmotionState));

    connectSignal(bridges.companionBridge?.stageModeChanged, () => scheduleSync("companion", syncCompanionState));
    connectSignal(bridges.companionBridge?.speechLevelChanged, () => scheduleSync("companion", syncCompanionState));
    connectSignal(bridges.companionBridge?.rendererChanged, () => scheduleSync("companion", syncCompanionState));

    connectSignal(bridges.windowBridge?.windowModeChanged, () => scheduleSync("window", syncWindowState));
    return true;
  }

  const derived = {
    stateLabel: computed(() => STATUS_LABELS[state.runtime.state] || state.runtime.state || "\u9759\u7f6e"),
    chatStageLabel: computed(() => STATUS_LABELS[state.chat.phase] || state.chat.phase || "\u9759\u7f6e"),
    moodLabel: computed(() => MOOD_LABELS[state.emotion.mood] || state.emotion.mood || "\u9759\u7f6e"),
    ambientModeLabel: computed(() => AMBIENT_MODE_LABELS[state.app.ambientMode] || "\u9759\u8c27"),
    progressRatio: computed(() => {
      if (state.runtime.progressTotal > 0) {
        return clamp01(state.runtime.progressStep / state.runtime.progressTotal);
      }
      return state.runtime.loaded ? 1 : 0;
    }),
    progressPercent: computed(() => Math.round(derived.progressRatio.value * 100)),
    voicePercent: computed(() => Math.round(clamp01(state.chat.voiceLevel) * 100)),
    presencePercent: computed(() => Math.round(clamp01(state.emotion.presenceLevel) * 100)),
    breathPercent: computed(() => Math.round(clamp01(state.emotion.breathLevel) * 100)),
    storagePercent: computed(() => Math.round(clamp01(state.runtime.storageUsageRatio) * 100)),
    conversationReady: computed(() => state.runtime.loaded || state.chat.ready),
    entryLabel: computed(() => (derived.conversationReady.value ? "\u5f00\u59cb\u5bf9\u8bdd" : "\u5524\u9192\u6838\u5fc3")),
    entryCaption: computed(() => (derived.conversationReady.value ? "Begin Conversation" : "Wake The Core")),
    presenceCopy: computed(() => {
      if (state.chat.phase === "replying") {
        return "Lumi \u6b63\u5728\u56de\u5e94\u4f60\u3002";
      }
      if (state.chat.running || state.emotion.isListening) {
        return "Lumi \u6b63\u5728\u503e\u542c\u3002";
      }
      if (derived.conversationReady.value) {
        return "Lumi \u5df2\u7ecf\u5728\u8fd9\u91cc\u3002";
      }
      return "Lumi \u6b63\u5728\u9759\u9759\u5730\u8fce\u5019\u4f60\u3002";
    }),
    bootPhaseCopy: computed(() => BOOT_PHASE_COPY[state.boot.phase] || "Preparing"),
    shortLogs: computed(() => state.runtime.logs.slice(-4)),
    currentModelName: computed(() => pickSelected(state.runtime.modelCatalog.llm)?.title || "Qwen 2.5"),
    currentAsrName: computed(() => pickSelected(state.runtime.modelCatalog.asr)?.title || "Listening Node"),
    currentTtsName: computed(() => pickSelected(state.runtime.modelCatalog.tts)?.title || "Voice Node"),
    currentReferenceName: computed(() => basename(state.runtime.selectedRefAudio) || "Reference Audio"),
    runtimePulse: computed(() =>
      Math.max(clamp01(state.chat.voiceLevel), clamp01(state.companion.speechLevel), derived.progressRatio.value)
    ),
    drawerData: computed(() => {
      const catalog = state.runtime.modelCatalog;
      const selectedMap = {
        asr: state.runtime.selectedAsr,
        llm: state.runtime.selectedLlm,
        tts: state.runtime.selectedTts,
        reference: state.runtime.selectedRefAudio
      };

      if (state.ui.drawerNode === "reference") {
        return {
          type: "reference",
          title: "\u8bb0\u5fc6\u6837\u672c",
          name: basename(state.runtime.selectedRefAudio) || "Reference Audio",
          caption: state.runtime.selectedRefText || "\u5728\u6bcf\u4e00\u4e2a\u5b89\u9759\u7684\u591c\u91cc\uff0cLumi \u90fd\u4f1a\u5728\u8fd9\u91cc\u7b49\u4f60\u3002",
          path: state.runtime.selectedRefAudio,
          options: catalog.reference || []
        };
      }

      const entries = catalog[state.ui.drawerNode] || [];
      const activePath = selectedMap[state.ui.drawerNode] || "";
      const activeEntry = entries.find((entry) => entry.path === activePath) || entries[0] || null;
      const drawerMeta = {
        asr: { title: "\u542c\u89c9\u8282\u70b9", fallback: "Listening Node", caption: "\u8d1f\u8d23\u542c\u89c1\u4f60\u8f7b\u58f0\u8bf4\u51fa\u7684\u6bcf\u4e00\u4e2a\u5f00\u7aef\u3002" },
        llm: { title: "\u601d\u7ef4\u6838\u5fc3", fallback: "Reasoning Core", caption: "\u8d1f\u8d23\u6574\u7406\u8bed\u4e49\u3001\u8bb0\u5fc6\u4e0e\u56de\u5e94\u610f\u613f\u3002" },
        tts: { title: "\u58f0\u7ebf\u8282\u70b9", fallback: "Voice Node", caption: "\u8d1f\u8d23\u8ba9\u56de\u5e94\u62e5\u6709\u53ef\u88ab\u8fa8\u8ba4\u7684\u58f0\u7ebf\u3002" }
      };
      const meta = drawerMeta[state.ui.drawerNode] || {
        title: "\u8282\u70b9\u8be6\u60c5",
        fallback: "Node",
        caption: "\u8282\u70b9\u4ecd\u5728\u7b49\u5f85\u4e0b\u4e00\u6b21\u88ab\u5524\u9192\u3002"
      };

      return {
        type: state.ui.drawerNode,
        title: meta.title,
        name: activeEntry?.title || meta.fallback,
        caption: activeEntry?.subtitle || meta.caption,
        path: activeEntry?.path || activePath,
        options: entries
      };
    })
  };

  const bridgeActions = {
    async notifyFrontendReady() {
      return Boolean(await callQt(bridges.shellBridge, "frontendReady"));
    },
    async loadModels() {
      return Boolean(await callQt(bridges.modelBridge, "loadSelectedModels"));
    },
    async switchModels() {
      await callQt(bridges.modelBridge, "switchSelectedModels");
      return true;
    },
    async releaseCache() {
      await callQt(bridges.modelBridge, "releaseCache");
      return true;
    },
    async scanModels() {
      await callQt(bridges.modelBridge, "scanModels");
      return true;
    },
    async scanComponents() {
      await callQt(bridges.modelBridge, "scanComponents");
      return true;
    },
    async openModelGalaxy() {
      await callQt(bridges.modelBridge, "openModelGalaxy");
      return true;
    },
    async startModelDownload(kind, provider, modelId, displayName) {
      return Boolean(await callQt(bridges.modelBridge, "startModelDownload", kind, provider, modelId, displayName));
    },
    async cancelModelDownload() {
      return Boolean(await callQt(bridges.modelBridge, "cancelModelDownload"));
    },
    async selectModel(type, path) {
      await callQt(bridges.modelBridge, "selectModel", type, path);
      return true;
    },
    async openLocalFolder(path) {
      return Boolean(await callQt(bridges.modelBridge, "openPath", path || derived.drawerData.value.path));
    },
    async startVoice() {
      return Boolean(await callQt(bridges.chatBridge, "startVoice"));
    },
    async stopVoice() {
      await callQt(bridges.chatBridge, "stopVoice");
      return true;
    },
    async clearChat() {
      await callQt(bridges.chatBridge, "clear");
      return true;
    },
    async sendCurrentText() {
      const text = state.ui.composerText.trim();
      if (!text) {
        return false;
      }
      await callQt(bridges.chatBridge, "sendText", text);
      state.ui.composerText = "";
      return true;
    },
    async saveSettings() {
      await callQt(
        bridges.appBridge,
        "saveSettings",
        state.app.language,
        state.app.checkUpdateOnStartup,
        state.app.startupPage,
        state.app.reduceMotion
      );
      return true;
    },
    async setAmbientMode(mode) {
      const normalized = String(mode || "quiet").trim().toLowerCase();
      state.app.ambientMode = normalized || "quiet";
      return Boolean(await callQt(bridges.appBridge, "setAmbientMode", normalized));
    },
    async setMood(mood) {
      await callQt(bridges.emotionBridge, "setMood", mood);
      return true;
    },
    async minimizeWindow() {
      return Boolean(await callQt(bridges.windowBridge, "minimize"));
    },
    async toggleWindowMode() {
      return Boolean(await callQt(bridges.windowBridge, "toggleWindowMode"));
    },
    async closeWindow() {
      return Boolean(await callQt(bridges.windowBridge, "close"));
    },
    async moveWindowBy(dx, dy) {
      return Boolean(await callQt(bridges.windowBridge, "moveBy", dx, dy));
    }
  };

  return {
    bridges,
    state,
    derived,
    initBridges,
    syncAll,
    bridgeActions
  };
}
