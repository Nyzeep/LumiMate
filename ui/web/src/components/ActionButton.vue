<script setup>
import { computed } from "vue";
import { useHoverIntent } from "../composables/useHoverIntent";

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
    required: true
  },
  tier: {
    type: String,
    default: "secondary"
  },
  semantic: {
    type: String,
    default: "core"
  },
  active: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

defineEmits(["click"]);

const { isEngaged, style, handlers } = useHoverIntent({
  disabled: computed(() => props.disabled)
});
</script>

<template>
  <button
    type="button"
    class="action-button"
    :class="[`action-button--${tier}`, `action-button--${semantic}`, { 'is-active': active, 'is-block': block }]"
    :disabled="disabled"
    :data-hovered="isEngaged ? 'true' : 'false'"
    :style="style"
    data-promoted-layer="true"
    v-on="handlers"
    @click.prevent="$emit('click')"
  >
    <span class="action-button__glow" aria-hidden="true"></span>
    <span class="action-button__glyph" aria-hidden="true">
      <svg viewBox="0 0 64 64">
        <circle cx="32" cy="32" r="22" />
        <circle cx="32" cy="32" r="13" />
        <path :d="iconPath" />
      </svg>
    </span>
    <span class="action-button__copy">
      <strong>{{ label }}</strong>
      <small v-if="subtitle">{{ subtitle }}</small>
    </span>
  </button>
</template>
