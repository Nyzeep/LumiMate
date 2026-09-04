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
      class="model-drawer-close-control"
      kind="icon"
      priority="quiet"
      accent="system"
      label="关闭配置"
      visually-hide-copy
      bare-glyph
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
      block
      @click="emit('open-path')"
    />
    <ControlGroup
      class="model-drawer__options"
      :items="optionItems"
      :selected-id="path"
      selection-role="radio"
      allow-empty
      block
      accent="model"
      :aria-label="optionsLabel"
      @select="emit('select', $event)"
    />
  </aside>
</template>

<style scoped>
.model-drawer-close-control {
  position: absolute;
  top: 16px;
  right: 16px;
  --glass-control-icon-inline-size: 34px;
  --glass-control-icon-block-size: 34px;
  --glass-control-icon-padding: 0;
  --glass-control-glyph-size: 18px;
}

.model-drawer__options {
  --glass-control-compact-min-block-size: 58px;
  --glass-control-compact-padding: 10px 14px;
  --glass-control-radius: 12px;
  --glass-control-justify-content: flex-start;
  --glass-control-label-font-size: var(--text-meta);
  --glass-control-subtitle-font-family: var(--font-mono);
  --glass-control-subtitle-font-size: var(--text-status);
  --glass-control-subtitle-letter-spacing: var(--tracking-mono);
  --glass-control-subtitle-text-transform: uppercase;
  display: grid;
  gap: 10px;
  margin-top: 24px;
  max-height: 40vh;
  overflow: auto;
  padding-right: 4px;
}
</style>
