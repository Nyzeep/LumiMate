<script setup>
import { computed } from "vue";
import { ICON_PATHS } from "../app/sceneRegistry";
import ControlGroup from "./ControlGroup.vue";

const props = defineProps({
  currentMode: {
    type: String,
    default: "quiet"
  }
});

const emit = defineEmits(["select"]);

const modes = [
  { id: "quiet", label: "静谧", subtitle: "Quiet", iconPath: ICON_PATHS.quiet },
  { id: "breath", label: "呼吸", subtitle: "Breath", iconPath: ICON_PATHS.breath },
  { id: "stream", label: "星流", subtitle: "Stream", iconPath: ICON_PATHS.stream }
];

const activeMode = computed(() => modes.find((mode) => mode.id === props.currentMode) || modes[0]);
</script>

<template>
  <div class="ambient-mode-switch" aria-label="环境模式控制" data-promoted-layer="true">
    <div class="ambient-mode-switch__shell">
      <ControlGroup
        class="ambient-mode-switch__group"
        :items="modes"
        :selected-id="currentMode"
        selection-role="radio"
        orientation="vertical"
        kind="icon"
        visually-hide-copy
        aria-label="环境模式"
        @select="emit('select', $event)"
      />
    </div>

    <div class="ambient-mode-switch__readout">
      <strong>{{ activeMode.label }}</strong>
      <small>{{ activeMode.subtitle }}</small>
    </div>
  </div>
</template>

<style scoped>
.ambient-mode-switch__group {
  --glass-control-icon-min-inline-size: 0;
  --glass-control-icon-min-block-size: 58px;
  --glass-control-icon-padding: 8px;
  --glass-control-glyph-size: 36px;
}
</style>
