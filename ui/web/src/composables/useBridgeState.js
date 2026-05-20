import { computed, reactive } from "vue";
import { ASSET_URLS } from "../app/sceneRegistry";
import {
  closeWindow,
  connectRuntimeEvents,
  getRuntimeState,
  minimizeWindow,
  runtimeCommand,
  shutdownBackend,
  toggleWindowMode
} from "../runtimeClient";

const STATUS_LABELS = {
  idle: "静置",
  validating: "校准",
  loading_asr: "听觉唤醒",
  loading_llm: "思维织入",
  loading_tts: "声线点亮",
  ready: "平静",
  listening: "倾听",
  thinking: "思索",
  replying: "回应",
  switching: "切换",
  releasing_cache: "释放缓存",
  checking_update: "检查更新",
  failed: "微暗"
};

const STEP_LABELS = {
  "loading.step.asr": "读取听觉节点",
  "loading.step.llm": "校准思维核心",
  "loading.step.tts": "点亮声线网络",
  "loading.step.reference": "对齐记忆样本"
};

const STORAGE_LABELS = {
  "storage.bucket.asr": "听觉模型层",
  "storage.bucket.llm": "思维核心层",
  "storage.bucket.tts": "声线模型层",
  "storage.bucket.genie": "对话记忆层",
  "storage.bucket.flash": "缓存预编译层"
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
  quiet: "静置",
  present: "在场",
  awakening: "苏醒",
  listening: "倾听",
  thinking: "思索",
  replying: "回应",
  dim: "微暗"
};

const AMBIENT_MODE_LABELS = {
  quiet: "静谧",
  breath: "呼吸",
  stream: "星流"
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
      title: entry.title || "未命名节点",
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
    .replace(/[A-Za-z]:[\\/][^\s,;:]+/g, "本地节点")
    .replace(/\/[^\s,;:]+\/[^\s,;:]+/g, "本地节点");
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
    return "由当前运行状态驱动的空间亮度与回应意愿。";
  }
  if (/load models|wake lumi/i.test(text)) {
    return "核心仍在静置，等待被唤醒。";
  }
  if (/listening/i.test(text)) {
    return "Lumi 正在倾听。";
  }
  if (/ready/i.test(text)) {
    return "Lumi 已经在这里。";
  }
  if (/quiet/i.test(text)) {
    return "空间回到安静。";
  }
  if (/response|shaping|thinking/i.test(text)) {
    return "回应正在成形。";
  }
  return text;
}

function assignScalar(target, key, value) {
  if (value !== undefined) {
    setIfChanged(target, key, value);
  }
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
      appAuthor: "Nyzeep",
      projectUrl: "https://github.com/Nyzeep/LumiMate",
      authorAvatarUrl: ASSET_URLS.authorAvatar,
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
      message: "Lumi 正在静静地迎候你",
      progressStep: 0,
      progressTotal: 0,
      progressMessage: "静置",
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
      status: "由当前运行状态驱动的空间亮度与回应意愿。",
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
      rendererCapability: "静态肖像、微光呼吸与声波脉冲"
    },
    window: {
      isFullscreen: false
    }
  });

  const bridges = reactive({});

  function applySnapshot(snapshot) {
    if (!snapshot || typeof snapshot !== "object") {
      return;
    }

    const boot = snapshot.boot || {};
    assignScalar(state.boot, "bridgeReady", Boolean(boot.bridgeReady ?? state.boot.bridgeReady));
    assignScalar(state.boot, "phase", boot.phase || state.boot.phase);
    assignScalar(state.boot, "ready", Boolean(boot.ready ?? state.boot.ready));

    const app = snapshot.app || {};
    assignScalar(state.app, "currentScene", app.currentScene);
    assignScalar(state.app, "currentSceneGroup", Number(app.currentSceneGroup ?? state.app.currentSceneGroup));
    assignScalar(state.app, "language", app.language);
    assignScalar(state.app, "startupPage", app.startupPage);
    assignScalar(state.app, "reduceMotion", Boolean(app.reduceMotion ?? state.app.reduceMotion));
    assignScalar(state.app, "checkUpdateOnStartup", Boolean(app.checkUpdateOnStartup ?? state.app.checkUpdateOnStartup));
    assignScalar(state.app, "ambientMode", app.ambientMode);
    assignScalar(state.app, "appVersion", app.appVersion);
    assignScalar(state.app, "appAuthor", app.appAuthor || "Nyzeep");
    assignScalar(state.app, "projectUrl", app.projectUrl || "https://github.com/Nyzeep/LumiMate");
    assignScalar(state.app, "authorAvatarUrl", app.authorAvatarUrl || ASSET_URLS.authorAvatar);
    assignScalar(state.app, "updateSource", app.updateSource);
    assignScalar(state.app, "projectRoot", app.projectRoot);
    assignScalar(state.app, "pythonExecutable", app.pythonExecutable);

    const runtime = snapshot.runtime || {};
    assignScalar(state.runtime, "state", runtime.state);
    assignScalar(state.runtime, "message", softMessage(runtime.message));
    assignScalar(state.runtime, "progressStep", Number(runtime.progressStep || 0));
    assignScalar(state.runtime, "progressTotal", Number(runtime.progressTotal || 0));
    assignScalar(state.runtime, "progressMessage", softMessage(runtime.progressMessage || runtime.message));
    assignScalar(state.runtime, "loaded", Boolean(runtime.loaded ?? state.runtime.loaded));
    state.runtime.logs = normalizeList(runtime.logs).map((item) => hidePaths(item));
    state.runtime.loadingSteps = normalizeList(runtime.loadingSteps).map((step) => ({
      label: STEP_LABELS[step.labelKey] || step.labelKey || "星线校准",
      done: Boolean(step.done),
      active: Boolean(step.active)
    }));
    state.runtime.modelCatalog = normalizeCatalog(runtime.modelCatalog);
    state.runtime.componentStatus = normalizeComponentStatus(runtime.componentStatus);
    state.runtime.downloadCatalog = normalizeDownloadCatalog(runtime.downloadCatalog);
    assignScalar(state.runtime, "downloadState", runtime.downloadState);
    assignScalar(state.runtime, "downloadProgress", Number(runtime.downloadProgress || 0));
    assignScalar(state.runtime, "downloadMessage", hidePaths(runtime.downloadMessage || "等待选择模型星系。"));
    state.runtime.downloadLogs = normalizeList(runtime.downloadLogs).map((item) => hidePaths(item)).filter(Boolean);
    state.runtime.storageItems = normalizeList(runtime.storageItems).map((item) => ({
      label: STORAGE_LABELS[item.titleKey] || item.titleKey || "本地资源",
      valueLabel: item.valueLabel || "0 GB",
      titleKey: item.titleKey || "",
      path: item.path || ""
    }));
    assignScalar(state.runtime, "storageUsedLabel", runtime.storageUsedLabel || "0 GB");
    assignScalar(state.runtime, "storageTotalLabel", runtime.storageTotalLabel || "0 GB");
    assignScalar(state.runtime, "storageFreeLabel", runtime.storageFreeLabel || "0 GB");
    assignScalar(state.runtime, "storageUsageRatio", Number(runtime.storageUsageRatio || 0));
    assignScalar(state.runtime, "selectedAsr", runtime.selectedAsr || "");
    assignScalar(state.runtime, "selectedLlm", runtime.selectedLlm || "");
    assignScalar(state.runtime, "selectedTts", runtime.selectedTts || "");
    assignScalar(state.runtime, "selectedRefAudio", runtime.selectedRefAudio || "");
    assignScalar(state.runtime, "selectedRefText", runtime.selectedRefText || "");
    assignScalar(state.runtime, "selectedTtsCharacter", runtime.selectedTtsCharacter || "");

    const chat = snapshot.chat || {};
    assignScalar(state.chat, "ready", Boolean(chat.ready ?? state.chat.ready));
    assignScalar(state.chat, "running", Boolean(chat.running ?? state.chat.running));
    assignScalar(state.chat, "status", softMessage(chat.status));
    assignScalar(state.chat, "phase", chat.phase || "idle");
    assignScalar(state.chat, "voiceLevel", clamp01(chat.voiceLevel));
    state.chat.messages = normalizeMessages(chat.messages);

    const emotion = snapshot.emotion || {};
    assignScalar(state.emotion, "mood", emotion.mood || "quiet");
    assignScalar(state.emotion, "breathLevel", clamp01(emotion.breathLevel || 0.52));
    assignScalar(state.emotion, "presenceLevel", clamp01(emotion.presenceLevel || 0.42));
    assignScalar(state.emotion, "isListening", Boolean(emotion.isListening));

    const companion = snapshot.companion || {};
    assignScalar(state.companion, "stageMode", companion.stageMode || "presence");
    assignScalar(state.companion, "speechLevel", clamp01(companion.speechLevel || 0));
    assignScalar(state.companion, "rendererType", companion.rendererType || "Portrait Stage");
    assignScalar(state.companion, "rendererCapability", companion.rendererCapability || "静态肖像、微光呼吸与声波脉冲");

    const windowState = snapshot.window || {};
    assignScalar(state.window, "isFullscreen", Boolean(windowState.isFullscreen));
  }

  async function initBridges() {
    try {
      const snapshot = await getRuntimeState();
      applySnapshot(snapshot);
      state.boot.bridgeReady = true;
      await connectRuntimeEvents((event) => {
        if (event?.state) {
          applySnapshot(event.state);
        }
      });
      return true;
    } catch (error) {
      console.warn("Unable to connect Lumi runtime.", error);
      return false;
    }
  }

  function syncAll() {
    return getRuntimeState().then(applySnapshot);
  }

  const derived = {
    stateLabel: computed(() => STATUS_LABELS[state.runtime.state] || state.runtime.state || "静置"),
    chatStageLabel: computed(() => STATUS_LABELS[state.chat.phase] || state.chat.phase || "静置"),
    moodLabel: computed(() => MOOD_LABELS[state.emotion.mood] || state.emotion.mood || "静置"),
    ambientModeLabel: computed(() => AMBIENT_MODE_LABELS[state.app.ambientMode] || "静谧"),
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
    entryLabel: computed(() => (derived.conversationReady.value ? "开始对话" : "唤醒核心")),
    entryCaption: computed(() => (derived.conversationReady.value ? "Begin Conversation" : "Wake The Core")),
    presenceCopy: computed(() => {
      if (state.chat.phase === "replying") {
        return "Lumi 正在回应你。";
      }
      if (state.chat.running || state.emotion.isListening) {
        return "Lumi 正在倾听。";
      }
      if (derived.conversationReady.value) {
        return "Lumi 已经在这里。";
      }
      return "Lumi 正在静静地迎候你。";
    }),
    bootPhaseCopy: computed(() => BOOT_PHASE_COPY[state.boot.phase] || "Preparing"),
    shortLogs: computed(() => state.runtime.logs.slice(-4)),
    currentModelName: computed(() => pickSelected(state.runtime.modelCatalog.llm)?.title || "Qwen 2.5"),
    currentAsrName: computed(() => pickSelected(state.runtime.modelCatalog.asr)?.title || "Listening Node"),
    currentTtsName: computed(() => pickSelected(state.runtime.modelCatalog.tts)?.title || "Voice Node"),
    currentReferenceName: computed(() => basename(state.runtime.selectedRefAudio) || "Reference Audio"),
    runtimePulse: computed(() => Math.max(clamp01(state.chat.voiceLevel), clamp01(state.companion.speechLevel), derived.progressRatio.value)),
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
          title: "记忆样本",
          name: basename(state.runtime.selectedRefAudio) || "Reference Audio",
          caption: state.runtime.selectedRefText || "在每一个安静的夜里，Lumi 都会在这里等你。",
          path: state.runtime.selectedRefAudio,
          options: catalog.reference || []
        };
      }

      const entries = catalog[state.ui.drawerNode] || [];
      const activePath = selectedMap[state.ui.drawerNode] || "";
      const activeEntry = entries.find((entry) => entry.path === activePath) || entries[0] || null;
      const drawerMeta = {
        asr: { title: "听觉节点", fallback: "Listening Node", caption: "负责听见你轻声说出的每一个开端。" },
        llm: { title: "思维核心", fallback: "Reasoning Core", caption: "负责整理语义、记忆与回应意愿。" },
        tts: { title: "声线节点", fallback: "Voice Node", caption: "负责让回应拥有可被辨认的声线。" }
      };
      const meta = drawerMeta[state.ui.drawerNode] || {
        title: "节点详情",
        fallback: "Node",
        caption: "节点仍在等待下一次被唤醒。"
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
      return runtimeCommand("/api/shell/frontend-ready");
    },
    async loadModels() {
      return runtimeCommand("/api/model/load");
    },
    async switchModels() {
      return runtimeCommand("/api/model/switch");
    },
    async releaseCache() {
      return runtimeCommand("/api/model/release-cache");
    },
    async scanModels() {
      return runtimeCommand("/api/model/scan");
    },
    async scanComponents() {
      return runtimeCommand("/api/model/scan-components");
    },
    async openModelGalaxy() {
      return runtimeCommand("/api/model/open-galaxy");
    },
    async startModelDownload(kind, provider, modelId, displayName) {
      return runtimeCommand("/api/model/download/start", { kind, provider, modelId, displayName });
    },
    async cancelModelDownload() {
      return runtimeCommand("/api/model/download/cancel");
    },
    async selectModel(type, path) {
      return runtimeCommand("/api/model/select", { type, path });
    },
    async openLocalFolder(path) {
      return runtimeCommand("/api/model/open-path", { path: path || derived.drawerData.value.path });
    },
    async startVoice() {
      return runtimeCommand("/api/chat/start-voice");
    },
    async stopVoice() {
      return runtimeCommand("/api/chat/stop-voice");
    },
    async clearChat() {
      return runtimeCommand("/api/chat/clear");
    },
    async sendCurrentText() {
      const text = state.ui.composerText.trim();
      if (!text) {
        return false;
      }
      const ok = await runtimeCommand("/api/chat/send-text", { text });
      if (ok) {
        state.ui.composerText = "";
      }
      return ok;
    },
    async saveSettings() {
      return runtimeCommand("/api/app/settings", {
        language: state.app.language,
        checkUpdateOnStartup: state.app.checkUpdateOnStartup,
        startupPage: state.app.startupPage,
        reduceMotion: state.app.reduceMotion
      });
    },
    async setAmbientMode(mode) {
      const normalized = String(mode || "quiet").trim().toLowerCase();
      state.app.ambientMode = normalized || "quiet";
      return runtimeCommand("/api/app/ambient-mode", { mode: normalized });
    },
    async setMood(mood) {
      return runtimeCommand("/api/emotion/mood", { mood });
    },
    minimizeWindow,
    toggleWindowMode,
    async closeWindow() {
      await shutdownBackend();
      return closeWindow();
    },
    async moveWindowBy() {
      return false;
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
