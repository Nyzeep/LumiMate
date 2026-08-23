<script setup>
import { computed, nextTick, onMounted, watch } from "vue";
import AmbientModeSwitch from "../components/AmbientModeSwitch.vue";
import BootVeil from "../components/BootVeil.vue";
import DiagnosticsHud from "../components/DiagnosticsHud.vue";
import ModelDrawer from "../components/ModelDrawer.vue";
import RailNav from "../components/RailNav.vue";
import RuntimeAmbientLayer from "../components/RuntimeAmbientLayer.vue";
import TechText from "../components/TechText.vue";
import { useBridgeState } from "../composables/useBridgeState";
import { useMotionPreferences } from "../composables/useMotionPreferences";
import { useRuntimeUiEngine } from "../composables/useRuntimeUiEngine";
import { useSceneNavigation } from "../composables/useSceneNavigation";
import { ICON_PATHS, SCENES } from "./sceneRegistry";

const FALLBACK_LOADING_STEPS = [
  { label: "\u8bfb\u53d6\u542c\u89c9\u8282\u70b9", threshold: 1, state: "loading_asr" },
  { label: "\u6821\u51c6\u601d\u7ef4\u6838\u5fc3", threshold: 2, state: "loading_llm" },
  { label: "\u70b9\u4eae\u58f0\u7ebf\u7f51\u7edc", threshold: 3, state: "loading_tts" },
  { label: "\u5bf9\u9f50\u8bb0\u5fc6\u6837\u672c", threshold: 4, state: "loading_tts" }
];

const { bridges, state, derived, initBridges, bridgeActions } = useBridgeState();
const {
  SCENE_GROUPS,
  activeScene,
  activeGroupScenes,
  backgroundLayers,
  activeBackgroundLayer,
  isTransitioning,
  sceneIs,
  primeBackgrounds,
  navigate,
  setSceneGroup,
  syncSceneFromBackend
} = useSceneNavigation(state, bridges);
const { reducedMotion } = useMotionPreferences(state);
const { shellClasses, ambientStyle, diagnostics, idle, timeLabel, timeSemantic, headerStatus, setAmbientMode: applyAmbientMode, noteActivity, activeSceneLabel } =
  useRuntimeUiEngine({
    state,
    derived,
    activeScene,
    isTransitioning,
    bridgeActions,
    reducedMotion
  });

const drawerData = derived.drawerData;
let bootFallbackTimer = 0;

const view = computed(() => ({
  stateLabel: derived.stateLabel.value,
  chatStageLabel: derived.chatStageLabel.value,
  moodLabel: derived.moodLabel.value,
  ambientModeLabel: derived.ambientModeLabel.value,
  progressRatio: derived.progressRatio.value,
  progressPercent: derived.progressPercent.value,
  voicePercent: derived.voicePercent.value,
  presencePercent: derived.presencePercent.value,
  breathPercent: derived.breathPercent.value,
  storagePercent: derived.storagePercent.value,
  conversationReady: derived.conversationReady.value,
  entryLabel: derived.entryLabel.value,
  entryCaption: derived.entryCaption.value,
  presenceCopy: derived.presenceCopy.value,
  bootPhaseCopy: derived.bootPhaseCopy.value,
  shortLogs: derived.shortLogs.value,
  currentModelName: derived.currentModelName.value,
  currentAsrName: derived.currentAsrName.value,
  currentTtsName: derived.currentTtsName.value,
  currentReferenceName: derived.currentReferenceName.value,
  runtimePulse: derived.runtimePulse.value,
  loadingSteps: state.runtime.loadingSteps.length
    ? state.runtime.loadingSteps
    : FALLBACK_LOADING_STEPS.map((step) => ({
        label: step.label,
        done: state.runtime.loaded || state.runtime.progressStep >= step.threshold,
        active: state.runtime.state === step.state
      })),
  modelCatalog: state.runtime.modelCatalog,
  runtimeMessage: state.runtime.message,
  storageItems: state.runtime.storageItems,
  storageUsedLabel: state.runtime.storageUsedLabel,
  storageTotalLabel: state.runtime.storageTotalLabel,
  storageFreeLabel: state.runtime.storageFreeLabel,
  isFullscreen: state.window.isFullscreen
}));

const windowDrag = {
  active: false,
  x: 0,
  y: 0,
  pointerId: null
};

async function beginConversation() {
  noteActivity();
  if (!view.value.conversationReady) {
    const started = await bridgeActions.loadModels();
    if (started) {
      await navigate("loading", true);
    }
    return;
  }
  const started = await bridgeActions.startVoice();
  if (started) {
    await navigate("chat", true);
  }
}

async function loadModels() {
  noteActivity();
  const started = await bridgeActions.loadModels();
  if (started) {
    await navigate("loading", true);
  }
}

async function switchModels() {
  noteActivity();
  await bridgeActions.switchModels();
  await navigate("loading", true);
}

const actions = {
  navigate,
  setSceneGroup,
  beginConversation,
  loadModels,
  switchModels,
  releaseCache: bridgeActions.releaseCache,
  scanModels: bridgeActions.scanModels,
  scanComponents: bridgeActions.scanComponents,
  openModelGalaxy: bridgeActions.openModelGalaxy,
  startModelDownload: bridgeActions.startModelDownload,
  cancelModelDownload: bridgeActions.cancelModelDownload,
  selectModel: bridgeActions.selectModel,
  openLocalFolder: bridgeActions.openLocalFolder,
  startVoice: bridgeActions.startVoice,
  stopVoice: bridgeActions.stopVoice,
  clearChat: bridgeActions.clearChat,
  agentStartTask: bridgeActions.agentStartTask,
  agentApprovePlan: bridgeActions.agentApprovePlan,
  agentApprovePermission: bridgeActions.agentApprovePermission,
  agentPauseTask: bridgeActions.agentPauseTask,
  agentResumeTask: bridgeActions.agentResumeTask,
  agentCancelTask: bridgeActions.agentCancelTask,
  agentResumeSession: bridgeActions.agentResumeSession,
  agentListSessions: bridgeActions.agentListSessions,
  async sendCurrentText() {
    noteActivity();
    await bridgeActions.sendCurrentText();
  },
  setComposerText(value) {
    noteActivity();
    state.ui.composerText = value;
  },
  openDrawer(type) {
    state.ui.drawerNode = type;
    state.ui.drawerOpen = true;
  },
  closeDrawer() {
    state.ui.drawerOpen = false;
  },
  async toggleLanguage() {
    state.app.language = state.app.language === "zh-CN" ? "en-US" : "zh-CN";
    await bridgeActions.saveSettings();
  },
  async toggleReduceMotion() {
    state.app.reduceMotion = !state.app.reduceMotion;
    await bridgeActions.saveSettings();
  },
  async toggleUpdateCheck() {
    state.app.checkUpdateOnStartup = !state.app.checkUpdateOnStartup;
    await bridgeActions.saveSettings();
  },
  async setAmbientMode(mode) {
    await applyAmbientMode(mode);
  },
  async setMood(mood) {
    await bridgeActions.setMood(mood);
  },
  minimizeWindow: bridgeActions.minimizeWindow,
  toggleWindowMode: bridgeActions.toggleWindowMode,
  closeWindow: bridgeActions.closeWindow
};

function beginWindowDrag(event) {
  if (state.window.isFullscreen || event.button !== 0 || event.target?.closest?.("button, input, textarea, select")) {
    return;
  }
  windowDrag.active = true;
  windowDrag.x = event.screenX;
  windowDrag.y = event.screenY;
  windowDrag.pointerId = event.pointerId;
  event.currentTarget?.setPointerCapture?.(event.pointerId);
}

async function dragWindow(event) {
  if (!windowDrag.active || state.window.isFullscreen) {
    return;
  }
  const dx = Math.round(event.screenX - windowDrag.x);
  const dy = Math.round(event.screenY - windowDrag.y);
  if (!dx && !dy) {
    return;
  }
  windowDrag.x = event.screenX;
  windowDrag.y = event.screenY;
  await bridgeActions.moveWindowBy(dx, dy);
}

function endWindowDrag(event) {
  if (!windowDrag.active) {
    return;
  }
  windowDrag.active = false;
  event.currentTarget?.releasePointerCapture?.(windowDrag.pointerId);
  windowDrag.pointerId = null;
}

function clearBootFallback() {
  if (bootFallbackTimer) {
    window.clearTimeout(bootFallbackTimer);
    bootFallbackTimer = 0;
  }
}

async function unlockBootFallback() {
  if (state.boot.ready) {
    return;
  }
  state.boot.phase = "revealed";
  state.boot.ready = true;
  if (state.boot.bridgeReady) {
    await Promise.race([
      bridgeActions.notifyFrontendReady(),
      new Promise((resolve) => window.setTimeout(resolve, 900))
    ]);
  }
}

watch(
  () => state.app.currentScene,
  () => {
    if (state.boot.bridgeReady) {
      void syncSceneFromBackend();
    }
  }
);

onMounted(async () => {
  bootFallbackTimer = window.setTimeout(() => {
    void unlockBootFallback();
  }, 2500);

  const ready = await initBridges();
  if (!ready) {
    await unlockBootFallback();
    return;
  }

  await Promise.race([primeBackgrounds(), new Promise((resolve) => window.setTimeout(resolve, 2200))]);
  await nextTick();
  await new Promise((resolve) => window.requestAnimationFrame(() => resolve()));
  await new Promise((resolve) => window.requestAnimationFrame(() => resolve()));
  await Promise.race([
    bridgeActions.notifyFrontendReady(),
    new Promise((resolve) => window.setTimeout(resolve, 1200))
  ]);
  await unlockBootFallback();
  clearBootFallback();
});
</script>

<template>
  <main class="app-shell" :class="shellClasses">
    <BootVeil :ready="state.boot.ready" :phase-label="view.bootPhaseCopy" />

    <div class="background-stage" aria-hidden="true">
      <div
        class="scene-background"
        :class="{ 'is-active': activeBackgroundLayer === 0 }"
        :style="{ backgroundImage: `url('${backgroundLayers[0]}')` }"
      ></div>
      <div
        class="scene-background"
        :class="{ 'is-active': activeBackgroundLayer === 1 }"
        :style="{ backgroundImage: `url('${backgroundLayers[1]}')` }"
      ></div>
      <div class="background-stage__veil"></div>
    </div>

    <RuntimeAmbientLayer :ambient-mode="state.app.ambientMode" :chat-phase="state.chat.phase" :idle="idle" :style="ambientStyle" />

    <div class="content-stage">
      <header class="shell-header">
        <div
          class="shell-drag-region"
          data-promoted-layer="true"
          @pointerdown="beginWindowDrag"
          @pointermove="dragWindow"
          @pointerup="endWindowDrag"
          @pointercancel="endWindowDrag"
          @pointerleave="endWindowDrag"
        >
          <TechText as="p" tone="muted" mono>LUMIMATE</TechText>
          <div class="shell-header__title-stack">
            <strong>{{ activeSceneLabel }}</strong>
            <small>{{ headerStatus }}</small>
          </div>
        </div>

        <p class="shell-header__time">
          <span>{{ timeSemantic }}</span>
          <span class="mono-inline">{{ timeLabel }}</span>
        </p>

        <div class="shell-header__actions" aria-label="窗口控制" data-promoted-layer="true">
          <button type="button" class="window-action" aria-label="最小化" @click.prevent="actions.minimizeWindow">
            <svg viewBox="0 0 24 24"><path :d="ICON_PATHS.minimize" /></svg>
          </button>
          <button
            type="button"
            class="window-action"
            :aria-label="state.window.isFullscreen ? '窗口化' : '全屏'"
            @click.prevent="actions.toggleWindowMode"
          >
            <svg viewBox="0 0 24 24"><path :d="state.window.isFullscreen ? ICON_PATHS.expand : ICON_PATHS.restore" /></svg>
          </button>
          <button type="button" class="window-action window-action--close" aria-label="关闭" @click.prevent="actions.closeWindow">
            <svg viewBox="0 0 24 24"><path :d="ICON_PATHS.close" /></svg>
          </button>
        </div>
      </header>

      <aside class="shell-side-controls" aria-label="侧边控制">
        <RailNav
          :groups="SCENE_GROUPS"
          :scenes="activeGroupScenes"
          :current-scene="state.app.currentScene"
          :current-group="state.app.currentSceneGroup"
          @navigate="actions.navigate"
          @select-group="actions.setSceneGroup"
        />

        <AmbientModeSwitch :current-mode="state.app.ambientMode" @select="actions.setAmbientMode" />
      </aside>

      <section class="scene-viewport" :class="{ 'is-transitioning': isTransitioning }">
        <component
          :is="scene.component"
          v-for="scene in SCENES"
          :key="scene.id"
          :scene="scene"
          :active="sceneIs(scene.id)"
          :state="state"
          :view="view"
          :actions="actions"
        />
      </section>
    </div>

    <ModelDrawer
      :open="state.ui.drawerOpen"
      :title="drawerData.title"
      :name="drawerData.name"
      :caption="drawerData.caption"
      :path="drawerData.path"
      :options="drawerData.options"
      @close="actions.closeDrawer"
      @open-path="actions.openLocalFolder(drawerData.path)"
      @select="(path) => actions.selectModel(drawerData.type, path)"
    />
    <button
      type="button"
      class="drawer-scrim"
      :class="{ 'is-open': state.ui.drawerOpen }"
      aria-label="关闭配置抽屉"
      @click.prevent="actions.closeDrawer"
    ></button>

    <DiagnosticsHud :visible="diagnostics.visible" :diagnostics="diagnostics" />
  </main>
</template>
