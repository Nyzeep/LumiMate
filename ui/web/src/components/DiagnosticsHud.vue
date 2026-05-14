<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  diagnostics: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <aside v-show="visible" class="diagnostics-hud" aria-live="polite">
    <p class="diagnostics-hud__title">Runtime Diagnostics</p>
    <dl class="diagnostics-hud__grid">
      <div>
        <dt>FPS</dt>
        <dd>{{ diagnostics.fps }}</dd>
      </div>
      <div>
        <dt>Animations</dt>
        <dd>{{ diagnostics.activeAnimations }}</dd>
      </div>
      <div>
        <dt>RAF Tasks</dt>
        <dd>{{ diagnostics.rafTaskCount }}</dd>
      </div>
      <div>
        <dt>Repaint Est.</dt>
        <dd>{{ diagnostics.repaintEstimate }}</dd>
      </div>
      <div>
        <dt>Observers</dt>
        <dd>{{ diagnostics.observerCount }}</dd>
      </div>
      <div>
        <dt>Layers</dt>
        <dd>{{ diagnostics.promotedLayerCount }}</dd>
      </div>
      <div>
        <dt>Idle</dt>
        <dd>{{ diagnostics.idle ? "Yes" : "No" }}</dd>
      </div>
    </dl>
  </aside>
</template>
