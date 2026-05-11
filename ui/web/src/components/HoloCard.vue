<template>
  <section class="holo-card" :class="toneClass">
    <slot />
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  tone: {
    type: String,
    default: "soft"
  }
});

const toneClass = computed(() => `holo-card--${props.tone}`);
</script>
