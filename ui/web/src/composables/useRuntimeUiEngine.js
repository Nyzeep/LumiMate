import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRuntimeDiagnostics } from "./useRuntimeDiagnostics";

function formatLocalTime(date) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(date);
}

function resolveTimeSemantic(hour) {
  if (hour >= 0 && hour < 5) {
    return "\u6df1\u591c";
  }
  if (hour >= 5 && hour < 8) {
    return "\u9ece\u660e";
  }
  return "\u591c\u665a";
}

function phaseBoost(phase) {
  switch (phase) {
    case "listening":
      return 0.28;
    case "thinking":
      return 0.2;
    case "replying":
      return 0.24;
    case "loading_asr":
    case "loading_llm":
    case "loading_tts":
    case "switching":
      return 0.22;
    default:
      return 0.08;
  }
}

function modeTuning(mode) {
  switch (mode) {
    case "stream":
      return { amplitude: 1.12, stream: 0.88, glow: 0.82 };
    case "breath":
      return { amplitude: 1.0, stream: 0.6, glow: 0.72 };
    default:
      return { amplitude: 0.74, stream: 0.32, glow: 0.54 };
  }
}

export function useRuntimeUiEngine({ state, derived, activeScene, isTransitioning, bridgeActions, reducedMotion }) {
  const { diagnostics, syncVisibility, toggleVisible, setIdle, registerAnimation, markPaint } = useRuntimeDiagnostics();

  const timeLabel = ref(formatLocalTime(new Date()));
  const timeSemantic = ref(resolveTimeSemantic(new Date().getHours()));
  const idle = ref(false);

  let lastActivityAt = Date.now();
  let lastPointerAt = 0;
  let timeTimer = 0;
  let idleTimer = 0;
  let releaseAmbientAnimation = null;

  function refreshTime() {
    const now = new Date();
    timeLabel.value = formatLocalTime(now);
    timeSemantic.value = resolveTimeSemantic(now.getHours());
  }

  function noteActivity(pointer = false) {
    const now = Date.now();
    if (pointer && now - lastPointerAt < 140) {
      return;
    }
    if (pointer) {
      lastPointerAt = now;
    }
    lastActivityAt = now;
    if (idle.value) {
      idle.value = false;
      setIdle(false);
    }
  }

  function checkIdle() {
    const idleNow = Date.now() - lastActivityAt >= 15000;
    if (idleNow !== idle.value) {
      idle.value = idleNow;
      setIdle(idleNow);
    }
  }

  function onPointerMove() {
    noteActivity(true);
  }

  function onPointerDown() {
    noteActivity();
  }

  function onKeydown(event) {
    noteActivity();
    if (event.ctrlKey && event.shiftKey && String(event.key).toLowerCase() === "d") {
      event.preventDefault();
      toggleVisible();
      markPaint(2);
    }
  }

  function setAmbientMode(mode) {
    noteActivity();
    return bridgeActions.setAmbientMode(mode);
  }

  watch(
    () => [
      state.chat.phase,
      state.chat.voiceLevel,
      state.runtime.state,
      state.runtime.progressStep,
      state.runtime.loaded,
      state.emotion.mood,
      state.emotion.breathLevel,
      state.emotion.presenceLevel,
      state.companion.speechLevel,
      state.app.currentScene
    ],
    () => {
      noteActivity();
    }
  );

  const ambientTuning = computed(() => modeTuning(state.app.ambientMode));
  const responseLevel = computed(
    () =>
      Math.max(
        derived.runtimePulse.value,
        state.chat.voiceLevel,
        state.companion.speechLevel,
        state.emotion.presenceLevel * 0.82
      ) + phaseBoost(state.chat.phase)
  );

  const shellClasses = computed(() => ({
    "is-idle": idle.value,
    "is-transitioning": isTransitioning.value,
    "is-windowed": !state.window.isFullscreen,
    [`ambient-mode--${state.app.ambientMode}`]: true,
    [`phase--${state.chat.phase || state.runtime.state}`]: true
  }));

  const ambientStyle = computed(() => {
    const idleScale = idle.value ? 0.72 : 1;
    const response = Math.min(1.36, responseLevel.value);
    return {
      "--motion-scale": reducedMotion.value ? "0" : "1",
      "--ambient-response": response.toFixed(3),
      "--ambient-amplitude": (ambientTuning.value.amplitude * idleScale).toFixed(3),
      "--ambient-stream": (ambientTuning.value.stream * idleScale).toFixed(3),
      "--ambient-glow": (ambientTuning.value.glow * idleScale).toFixed(3)
    };
  });

  const headerStatus = computed(() => {
    if (state.chat.phase === "replying") {
      return "\u56de\u5e94\u6b63\u5728\u6210\u5f62";
    }
    if (state.chat.phase === "thinking") {
      return "\u601d\u7eea\u6b63\u5728\u6c47\u805a";
    }
    if (state.chat.phase === "listening") {
      return "\u503e\u542c\u4e2d";
    }
    if (!derived.conversationReady.value) {
      return "\u7b49\u5f85\u5524\u9192";
    }
    return derived.stateLabel.value;
  });

  onMounted(() => {
    refreshTime();
    syncVisibility(false);
    timeTimer = window.setInterval(refreshTime, 30000);
    idleTimer = window.setInterval(checkIdle, 1000);
    releaseAmbientAnimation = registerAnimation("runtime-ambient");
    window.addEventListener("pointermove", onPointerMove, { passive: true });
    window.addEventListener("pointerdown", onPointerDown, { passive: true });
    window.addEventListener("keydown", onKeydown);
  });

  onBeforeUnmount(() => {
    if (timeTimer) {
      window.clearInterval(timeTimer);
    }
    if (idleTimer) {
      window.clearInterval(idleTimer);
    }
    if (releaseAmbientAnimation) {
      releaseAmbientAnimation();
    }
    window.removeEventListener("pointermove", onPointerMove);
    window.removeEventListener("pointerdown", onPointerDown);
    window.removeEventListener("keydown", onKeydown);
  });

  return {
    shellClasses,
    ambientStyle,
    diagnostics,
    idle,
    timeLabel,
    timeSemantic,
    headerStatus,
    setAmbientMode,
    noteActivity,
    activeSceneLabel: computed(() => activeScene.value.title)
  };
}
