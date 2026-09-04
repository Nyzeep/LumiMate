<script setup>
import { computed, nextTick, ref, watch } from "vue";
import ControlGroup from "./ControlGroup.vue";
import GlassControl from "./GlassControl.vue";

const CLOSE_PATH = "M6 6l12 12M18 6 6 18";

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ""
  },
  name: {
    type: String,
    default: ""
  },
  caption: {
    type: String,
    default: ""
  },
  path: {
    type: String,
    default: ""
  },
  options: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(["close", "select", "open-path"]);
const optionItems = computed(() => props.options.map((option) => ({
  id: option.path,
  label: option.title,
  subtitle: option.subtitle
})));
const optionsLabel = computed(() => (props.title ? props.title + " 可选配置" : "可选模型配置"));
const returnFocusTarget = ref(null);

watch(
  () => props.open,
  (isOpen) => {
    if (typeof document === "undefined") {
      return;
    }
    if (isOpen) {
      returnFocusTarget.value = document.activeElement instanceof HTMLElement ? document.activeElement : null;
      return;
    }
    const target = returnFocusTarget.value;
    if (target?.isConnected) {
      nextTick(() => target.focus());
    }
  }
);
</script>

<template>
  <aside class="model-drawer" :class="{ 'is-open': open }" :aria-hidden="!open" :inert="!open">
    <GlassControl
      class="model-drawer__close"
      kind="icon"
      priority="quiet"
      accent="system"
      label="关闭配置"
      :icon-path="CLOSE_PATH"
      @click="emit('close')"
    />
    <p class="scene-kicker">{{ title }}</p>
    <h2>{{ name }}</h2>
    <p class="panel-note">{{ caption }}</p>
    <div class="model-drawer__path">
      <span>本地位置</span>
      <code>{{ path || "尚未选择" }}</code>
    </div>
    <GlassControl
      class="model-drawer__open-path"
      kind="compact"
      priority="secondary"
      accent="model"
      label="打开本地文件夹"
      subtitle="Open folder"
      @click="emit('open-path')"
    />
    <ControlGroup
      class="model-drawer__options"
      :items="optionItems"
      :selected-id="path"
      selection-role="radio"
      allow-empty
      accent="model"
      :aria-label="optionsLabel"
      @select="emit('select', $event)"
    />
  </aside>
</template>

<style scoped>
.model-drawer__close {
  --glass-control-icon-min-inline-size: 34px;
  --glass-control-icon-min-block-size: 34px;
  width: 34px;
  min-width: 34px;
  padding: 0;
}

.model-drawer__close :deep(.glass-control__glyph) {
  width: 18px;
  border: 0;
  background: transparent;
}

.model-drawer__close :deep(.glass-control__copy) {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

.model-drawer__open-path {
  width: 100%;
}

.model-drawer__options {
  display: grid;
  gap: 10px;
  margin-top: 24px;
  max-height: 40vh;
  overflow: auto;
  padding-right: 4px;
}

.model-drawer__options :deep(.glass-control) {
  display: grid;
  gap: 4px;
  justify-items: start;
  width: 100%;
  min-height: 58px;
  padding: 10px 14px;
  border-radius: 12px;
  text-align: left;
}

.model-drawer__options :deep(.glass-control)::after {
  content: none;
}

.model-drawer__options :deep(.glass-control__copy strong) {
  color: var(--color-text);
  font-size: var(--text-meta);
}

.model-drawer__options :deep(.glass-control__copy small) {
  color: var(--color-dim);
  font-family: var(--font-mono);
  font-size: var(--text-status);
  letter-spacing: var(--tracking-mono);
  text-transform: uppercase;
}
</style>
