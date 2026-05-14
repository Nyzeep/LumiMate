import { computed, ref } from "vue";
import { useRuntimeDiagnostics } from "./useRuntimeDiagnostics";

export function useHoverIntent(options = {}) {
  const hovered = ref(false);
  const focused = ref(false);
  const pressed = ref(false);
  const disabled = computed(() => Boolean(options.disabled?.value ?? options.disabled ?? false));
  const { markPaint } = useRuntimeDiagnostics();

  function setHovering(value) {
    if (disabled.value) {
      return;
    }
    hovered.value = value;
    markPaint(1);
  }

  function onPointerEnter() {
    setHovering(true);
  }

  function onPointerLeave() {
    hovered.value = false;
    pressed.value = false;
  }

  function onFocus() {
    if (disabled.value) {
      return;
    }
    focused.value = true;
  }

  function onBlur() {
    focused.value = false;
    pressed.value = false;
  }

  function onPointerDown() {
    if (disabled.value) {
      return;
    }
    pressed.value = true;
  }

  function onPointerUp() {
    pressed.value = false;
  }

  const intent = computed(() => (hovered.value || focused.value ? 1 : 0));
  const press = computed(() => (pressed.value ? 1 : 0));
  const isEngaged = computed(() => hovered.value || focused.value || pressed.value);
  const style = computed(() => ({
    "--hover-intent": String(intent.value),
    "--press-intent": String(press.value)
  }));

  return {
    hovered,
    focused,
    pressed,
    isEngaged,
    style,
    handlers: {
      onPointerenter: onPointerEnter,
      onPointerleave: onPointerLeave,
      onFocus,
      onBlur,
      onPointerdown: onPointerDown,
      onPointerup: onPointerUp
    }
  };
}
