<script setup>
import { useHoverIntent } from "../composables/useHoverIntent";

defineProps({
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
  active: {
    type: Boolean,
    default: false
  }
});

defineEmits(["click"]);

const { isEngaged, style, handlers } = useHoverIntent();
</script>

<template>
  <button
    type="button"
    class="orbital-icon-button"
    :class="[`orbital-icon-button--${semantic}`, { 'is-active': active }]"
    :data-hovered="isEngaged ? 'true' : 'false'"
    :style="style"
    data-promoted-layer="true"
    v-on="handlers"
    @click.prevent="$emit('click')"
  >
    <span class="orbital-icon-button__halo" aria-hidden="true">
      <span class="orbital-icon-button__glow"></span>
      <svg viewBox="0 0 24 24">
        <path :d="iconPath" />
      </svg>
    </span>
    <span class="orbital-icon-button__label">{{ label }}</span>
  </button>
</template>
