import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

export function useMotionPreferences(state) {
  const systemReduceMotion = ref(false);
  let mediaQuery = null;
  let handler = null;

  onMounted(() => {
    if (typeof window === "undefined" || !window.matchMedia) {
      return;
    }
    mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    systemReduceMotion.value = mediaQuery.matches;
    handler = (event) => {
      systemReduceMotion.value = event.matches;
    };
    mediaQuery.addEventListener?.("change", handler);
    mediaQuery.addListener?.(handler);
  });

  onBeforeUnmount(() => {
    mediaQuery?.removeEventListener?.("change", handler);
    mediaQuery?.removeListener?.(handler);
  });

  const reducedMotion = computed(() => Boolean(state.app.reduceMotion || systemReduceMotion.value));

  watch(
    reducedMotion,
    (value) => {
      document.documentElement.classList.toggle("reduced-motion", value);
    },
    { immediate: true }
  );

  return { reducedMotion };
}
