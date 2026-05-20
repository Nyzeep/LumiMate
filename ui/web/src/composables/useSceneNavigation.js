import { computed, reactive, ref } from "vue";
import { getSceneBackground, getSceneById, SCENES, SCENE_GROUPS } from "../app/sceneRegistry";
import { runtimeCommand } from "../runtimeClient";

const NAVIGATION_THROTTLE_MS = 240;
const TRANSITION_LOCK_MS = 360;

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

export function useSceneNavigation(state) {
  const backgroundCache = reactive({});
  const preloadCache = reactive({});
  const homeBackground = getSceneBackground("home");
  const backgroundLayers = ref([homeBackground, homeBackground]);
  const activeBackgroundLayer = ref(0);
  const isTransitioning = ref(false);

  let backgroundToken = 0;
  let nextNavigationAt = 0;
  let unlockTimer = 0;

  const activeScene = computed(() => getSceneById(state.app.currentScene));
  const activeGroupScenes = computed(() => SCENES.filter((scene) => scene.group === state.app.currentSceneGroup));

  function sceneIs(sceneId) {
    return state.app.currentScene === sceneId;
  }

  function resolveSceneBackground(sceneId) {
    if (!backgroundCache[sceneId]) {
      backgroundCache[sceneId] = getSceneBackground(sceneId);
    }
    return backgroundCache[sceneId];
  }

  async function prepareSceneBackground(sceneId) {
    const url = resolveSceneBackground(sceneId);
    if (!preloadCache[url]) {
      preloadCache[url] = preloadImage(url);
    }
    await preloadCache[url];
    return url;
  }

  function lockTransition() {
    isTransitioning.value = true;
    window.clearTimeout(unlockTimer);
    unlockTimer = window.setTimeout(() => {
      isTransitioning.value = false;
    }, TRANSITION_LOCK_MS);
  }

  async function swapSceneBackground(sceneId, immediate = false) {
    const token = backgroundToken + 1;
    backgroundToken = token;

    const url = await prepareSceneBackground(sceneId);
    if (backgroundToken !== token || backgroundLayers.value[activeBackgroundLayer.value] === url) {
      return;
    }

    const nextLayer = activeBackgroundLayer.value === 0 ? 1 : 0;
    backgroundLayers.value = backgroundLayers.value.map((current, index) => (index === nextLayer ? url : current));

    if (immediate) {
      activeBackgroundLayer.value = nextLayer;
      return;
    }

    window.requestAnimationFrame(() => {
      activeBackgroundLayer.value = nextLayer;
    });
  }

  async function primeBackgrounds() {
    await swapSceneBackground(state.app.currentScene, true);
    void Promise.all(SCENES.map((scene) => prepareSceneBackground(scene.id)));
  }

  async function navigate(sceneId, force = false) {
    const scene = getSceneById(sceneId);
    if (scene.id === state.app.currentScene && !force) {
      return false;
    }

    const now = Date.now();
    if (!force && now < nextNavigationAt) {
      return false;
    }

    nextNavigationAt = now + NAVIGATION_THROTTLE_MS;
    lockTransition();
    await prepareSceneBackground(scene.id);
    state.app.currentScene = scene.id;
    state.app.currentSceneGroup = scene.group;

    await swapSceneBackground(scene.id);
    await runtimeCommand("/api/app/navigate", { scene: scene.id });
    return true;
  }

  async function setSceneGroup(groupIndex) {
    const normalizedGroup = Number(groupIndex);
    if (normalizedGroup === state.app.currentSceneGroup) {
      return false;
    }

    const targetScene = SCENES.find((scene) => scene.group === normalizedGroup) || SCENES[0];
    lockTransition();
    await prepareSceneBackground(targetScene.id);
    state.app.currentSceneGroup = normalizedGroup;
    state.app.currentScene = targetScene.id;

    await swapSceneBackground(targetScene.id);
    await runtimeCommand("/api/app/scene-group", { groupIndex: normalizedGroup });
    return true;
  }

  async function syncSceneFromBackend() {
    await swapSceneBackground(state.app.currentScene);
  }

  return {
    SCENES,
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
  };
}
