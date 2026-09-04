<script setup>
import { computed } from "vue";
import GlassControl from "./GlassControl.vue";

defineOptions({ inheritAttrs: false });

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ""
  },
  iconPath: {
    type: String,
    default: ""
  },
  tier: {
    type: String,
    default: "secondary"
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
  block: {
    type: Boolean,
    default: false
  },
  truncateCopy: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["click"]);
const priority = computed(() => (["primary", "quiet"].includes(props.tier) ? props.tier : "secondary"));
const selected = computed(() => (props.active ? true : null));
</script>

<template>
  <GlassControl
    v-bind="$attrs"
    kind="card"
    :label="label"
    :subtitle="subtitle"
    :icon-path="iconPath"
    icon-view-box="0 0 64 64"
    :priority="priority"
    :intent="intent"
    :accent="semantic"
    :disabled="disabled"
    :selected="selected"
    :block="block"
    :truncate-copy="truncateCopy"
    @click="emit('click', $event)"
  />
</template>
