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
.ambient-mode-switch__group :deep(.glass-control--icon) {
  --glass-control-icon-min-inline-size: 0;
  --glass-control-icon-min-block-size: 58px;
  padding: 8px;
}

.ambient-mode-switch__group :deep(.glass-control__glyph) {
  width: 36px;
}

.ambient-mode-switch__group :deep(.glass-control__copy) {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}
</style>
