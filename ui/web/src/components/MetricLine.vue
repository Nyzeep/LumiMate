<template>
  <div class="metric-line">
    <div class="metric-line__row">
      <span>{{ label }}</span>
      <strong>{{ value }}</strong>
    </div>
    <div class="metric-line__track">
      <span :style="{ transform: `scaleX(${progress})` }"></span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  progress: {
    type: Number,
    default: 0
  }
});
</script>
