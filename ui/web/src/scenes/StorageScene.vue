<script setup>
import GlassControl from "../components/GlassControl.vue";
import HoloCard from "../components/HoloCard.vue";
import MetricLine from "../components/MetricLine.vue";
import OrbitLoading from "../components/OrbitLoading.vue";
import TechText from "../components/TechText.vue";

defineProps({
  scene: { type: Object, required: true },
  active: { type: Boolean, default: false },
  state: { type: Object, required: true },
  view: { type: Object, required: true },
  actions: { type: Object, required: true }
});
</script>

<template>
  <section class="scene-panel scene-panel--storage" :class="{ 'is-active': active }" aria-label="存储">
    <div class="scene-ambient scene-ambient--storage" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-4 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">容量观测</h2>
        <p class="scene-summary">观察模型、记忆与缓存的占用关系，让维护动作仍然留在安静且安全的工作流里。</p>
      </div>

      <div class="span-3">
        <OrbitLoading :progress="view.storagePercent / 100" :loaded="view.storagePercent > 0" caption="Storage" label="存储轨道" variant="storage" />
      </div>

      <div class="span-5">
        <HoloCard class="info-card" tone="strong">
          <h2 class="metric-display">{{ view.storageUsedLabel }} <small>/ {{ view.storageTotalLabel }}</small></h2>
          <MetricLine label="已追踪容量" :value="`${view.storagePercent}%`" :progress="view.storagePercent / 100" />
          <MetricLine label="剩余空间" :value="view.storageFreeLabel" :progress="Math.max(0, 1 - view.storagePercent / 100)" />
        </HoloCard>
      </div>

      <div class="span-12">
        <HoloCard class="bucket-card">
          <div v-for="item in view.storageItems" :key="item.titleKey || item.path" class="bucket-row">
            <span>{{ item.label }}</span>
            <strong>{{ item.valueLabel }}</strong>
          </div>
        </HoloCard>
      </div>

      <div class="span-12 action-row">
        <GlassControl
          label="安全释放缓存"
          subtitle="Release cache"
          kind="compact"
          priority="quiet"
          intent="danger"
          accent="system"
          @click="actions.releaseCache"
        />
      </div>
    </div>
  </section>
</template>
