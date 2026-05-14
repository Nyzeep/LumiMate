<script setup>
import { computed } from "vue";
import { ICON_PATHS } from "../app/sceneRegistry";

const props = defineProps({
  currentMode: {
    type: String,
    default: "quiet"
  }
});

defineEmits(["select"]);

const modes = [
  { id: "quiet", label: "\u9759\u8c27", subtitle: "Quiet", iconPath: ICON_PATHS.quiet },
  { id: "breath", label: "\u547c\u5438", subtitle: "Breath", iconPath: ICON_PATHS.breath },
  { id: "stream", label: "\u661f\u6d41", subtitle: "Stream", iconPath: ICON_PATHS.stream }
];

const activeMode = computed(() => modes.find((mode) => mode.id === props.currentMode) || modes[0]);
</script>

<template>
  <div class="ambient-mode-switch" aria-label="环境模式控制" data-promoted-layer="true">
    <div class="ambient-mode-switch__shell">
      <button
        v-for="mode in modes"
        :key="mode.id"
        type="button"
        class="ambient-mode-switch__button"
        :class="{ 'is-active': currentMode === mode.id }"
        :aria-label="mode.label"
        :title="mode.label"
        @click.prevent="$emit('select', mode.id)"
      >
        <span class="ambient-mode-switch__glow" aria-hidden="true"></span>
        <span class="ambient-mode-switch__core" aria-hidden="true">
          <span class="ambient-mode-switch__orbit"></span>
          <svg viewBox="0 0 24 24">
            <path :d="mode.iconPath" />
          </svg>
        </span>
      </button>
    </div>

    <div class="ambient-mode-switch__readout">
      <strong>{{ activeMode.label }}</strong>
      <small>{{ activeMode.subtitle }}</small>
    </div>
  </div>
</template>
