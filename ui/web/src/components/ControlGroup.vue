<script setup>
import { computed, nextTick, ref } from "vue";
import GlassControl from "./GlassControl.vue";

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  selectedId: {
    type: String,
    default: ""
  },
  selectionRole: {
    type: String,
    default: "radio",
    validator: (value) => ["radio", "tab"].includes(value)
  },
  orientation: {
    type: String,
    default: "horizontal",
    validator: (value) => ["horizontal", "vertical"].includes(value)
  },
  kind: {
    type: String,
    default: "compact"
  },
  accent: {
    type: String,
    default: "core"
  },
  ariaLabel: {
    type: String,
    required: true
  }
});

const emit = defineEmits(["select"]);
const controlRefs = ref([]);
const selectedIndex = computed(() => Math.max(0, props.items.findIndex((item) => item.id === props.selectedId)));
const groupRole = computed(() => (props.selectionRole === "tab" ? "tablist" : "radiogroup"));

function isSelected(index) {
  return index === selectedIndex.value;
}

function setControlRef(element, index) {
  controlRefs.value[index] = element;
}

function selectItem(item) {
  emit("select", item.id);
}

function focusItem(index) {
  nextTick(() => {
    const control = controlRefs.value[index];
    const element = control?.$el || control;
    element?.focus?.();
  });
}

function moveSelection(event, index) {
  const { key } = event;
  const lastIndex = props.items.length - 1;
  let nextIndex = index;

  if (key === "ArrowRight" || key === "ArrowDown") {
    nextIndex = index === lastIndex ? 0 : index + 1;
  } else if (key === "ArrowLeft" || key === "ArrowUp") {
    nextIndex = index === 0 ? lastIndex : index - 1;
  } else if (key === "Home") {
    nextIndex = 0;
  } else if (key === "End") {
    nextIndex = lastIndex;
  } else {
    return;
  }

  event.preventDefault();
  const item = props.items[nextIndex];
  if (!item) {
    return;
  }
  selectItem(item);
  focusItem(nextIndex);
}
</script>

<template>
  <div
    class="control-group"
    :class="{
      'control-group--tab': selectionRole === 'tab',
      'control-group--radio': selectionRole === 'radio',
      'control-group--horizontal': orientation === 'horizontal',
      'control-group--vertical': orientation === 'vertical'
    }"
    :role="groupRole"
    :aria-label="ariaLabel"
    :aria-orientation="orientation"
  >
    <GlassControl
      v-for="(item, index) in items"
      :key="item.id"
      :ref="(element) => setControlRef(element, index)"
      :kind="kind"
      :label="item.label"
      :subtitle="item.subtitle"
      :icon-path="item.iconPath"
      :accent="accent"
      :selected="isSelected(index)"
      :selection-role="selectionRole"
      :aria-controls="selectionRole === 'tab' ? item.panelId : undefined"
      :tabindex="isSelected(index) ? 0 : -1"
      @click="selectItem(item)"
      @keydown="moveSelection($event, index)"
    />
  </div>
</template>

<style scoped>
.control-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.control-group--vertical {
  flex-direction: column;
  flex-wrap: nowrap;
}

.control-group--vertical :deep(.glass-control) {
  width: 100%;
}
</style>
