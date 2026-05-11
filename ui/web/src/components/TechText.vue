<template>
  <component :is="as" class="tech-text" :class="[`tech-text--${tone}`, { 'tech-text--mono': mono }]">
    <slot />
  </component>
</template>

<script setup>
defineProps({
  as: {
    type: String,
    default: "span"
  },
  tone: {
    type: String,
    default: "primary"
  },
  mono: {
    type: Boolean,
    default: false
  }
});
</script>
