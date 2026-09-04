<script setup>
import { computed } from "vue";
import GlassControl from "./GlassControl.vue";

defineOptions({ inheritAttrs: false });

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  iconPath: {
    type: String,
    required: true
  },
  semantic: {
    type: String,
    default: "core"
  },
  intent: {
    type: String,
    default: "neutral"
  },
  active: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["click"]);
const selected = computed(() => (props.active ? true : null));
</script>

<template>
  <GlassControl
    v-bind="$attrs"
    kind="icon"
    :label="label"
    :icon-path="iconPath"
    :accent="semantic"
    :intent="intent"
    :disabled="disabled"
    :selected="selected"
    @click="emit('click', $event)"
  />
</template>
