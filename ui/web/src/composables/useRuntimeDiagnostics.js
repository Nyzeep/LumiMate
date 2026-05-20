import { computed, reactive } from "vue";

const diagnosticsState = reactive({
  fps: 0,
  activeAnimations: 0,
  rafTaskCount: 0,
  repaintEstimate: 0,
  observerCount: 0,
  promotedLayerCount: 0,
  idle: false,
  visible: false
});

const rafTasks = new Map();
const animationLabels = new Set();
let diagnosticsStarted = false;
let previousFrameAt = 0;
let frameCount = 0;
let sampleStartedAt = 0;
let nextTaskId = 1;
let frameId = 0;

function readQueryFlag() {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    const params = new URLSearchParams(window.location.search);
    return params.get("diag") === "1";
  } catch {
    return false;
  }
}

function sampleDom() {
  if (typeof document === "undefined") {
    return;
  }
  diagnosticsState.promotedLayerCount = document.querySelectorAll("[data-promoted-layer='true']").length;
  if (typeof document.getAnimations === "function") {
    diagnosticsState.activeAnimations = document.getAnimations().filter((animation) => animation.playState === "running").length;
  } else {
    diagnosticsState.activeAnimations = animationLabels.size;
  }
}

function startLoop() {
  if (diagnosticsStarted || typeof window === "undefined") {
    return;
  }
  diagnosticsStarted = true;
  sampleStartedAt = performance.now();

  const tick = (now) => {
    frameCount += 1;
    if (sampleStartedAt === 0) {
      sampleStartedAt = now;
    }
    if (now - sampleStartedAt >= 1000) {
      diagnosticsState.fps = Math.round((frameCount * 1000) / (now - sampleStartedAt));
      frameCount = 0;
      sampleStartedAt = now;
      sampleDom();
    }
    previousFrameAt = now;
    frameId = window.requestAnimationFrame(tick);
  };

  frameId = window.requestAnimationFrame(tick);
}

function stopLoop() {
  if (!diagnosticsStarted || typeof window === "undefined") {
    return;
  }
  diagnosticsStarted = false;
  if (frameId) {
    window.cancelAnimationFrame(frameId);
    frameId = 0;
  }
  previousFrameAt = 0;
  frameCount = 0;
  sampleStartedAt = 0;
  diagnosticsState.fps = 0;
}

export function useRuntimeDiagnostics() {
  const baseVisible = import.meta.env.DEV || readQueryFlag();

  function setVisible(value) {
    diagnosticsState.visible = Boolean(value);
    if (diagnosticsState.visible) {
      startLoop();
    } else if (!baseVisible) {
      stopLoop();
    }
  }

  function syncVisibility(force) {
    setVisible(baseVisible || force);
  }

  function toggleVisible() {
    setVisible(!diagnosticsState.visible);
  }

  function setIdle(value) {
    diagnosticsState.idle = Boolean(value);
  }

  function registerRafTask(label = "runtime") {
    const id = `${label}:${nextTaskId++}`;
    rafTasks.set(id, label);
    diagnosticsState.rafTaskCount = rafTasks.size;
    return () => {
      if (rafTasks.delete(id)) {
        diagnosticsState.rafTaskCount = rafTasks.size;
      }
    };
  }

  function markPaint(amount = 1) {
    diagnosticsState.repaintEstimate += amount;
  }

  function registerAnimation(label = "ambient") {
    animationLabels.add(label);
    diagnosticsState.activeAnimations = Math.max(diagnosticsState.activeAnimations, animationLabels.size);
    return () => {
      animationLabels.delete(label);
      diagnosticsState.activeAnimations = Math.max(animationLabels.size, diagnosticsState.activeAnimations - 1);
    };
  }

  function trackObserver(delta) {
    diagnosticsState.observerCount = Math.max(0, diagnosticsState.observerCount + Number(delta || 0));
  }

  return {
    diagnostics: computed(() => diagnosticsState),
    syncVisibility,
    toggleVisible,
    setIdle,
    registerRafTask,
    registerAnimation,
    markPaint,
    trackObserver
  };
}
