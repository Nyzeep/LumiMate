<template>
  <div class="boot-veil" :class="{ 'is-hidden': ready }" aria-hidden="true">
    <div class="boot-veil__core">
      <div class="boot-veil__rings">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <div class="boot-veil__copy">
        <p class="boot-veil__eyebrow">LumiMate</p>
        <strong>{{ title }}</strong>
        <small>{{ phaseLabel }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  ready: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: "正在展开空间"
  },
  phaseLabel: {
    type: String,
    default: "Gathering starlight"
  }
});
</script>
