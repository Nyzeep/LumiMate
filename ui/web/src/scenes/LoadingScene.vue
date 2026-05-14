<script setup>
import ActionButton from "../components/ActionButton.vue";
import HoloCard from "../components/HoloCard.vue";
import MetricLine from "../components/MetricLine.vue";
import OrbitLoading from "../components/OrbitLoading.vue";
import TechText from "../components/TechText.vue";
import { ICON_PATHS } from "../app/sceneRegistry";

defineProps({
  scene: { type: Object, required: true },
  active: { type: Boolean, default: false },
  state: { type: Object, required: true },
  view: { type: Object, required: true },
  actions: { type: Object, required: true }
});
</script>

<template>
  <section class="scene-panel scene-panel--loading" :class="{ 'is-active': active }" aria-label="加载空间">
    <div class="scene-ambient scene-ambient--loading" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-4 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">苏醒过程</h2>
        <p class="scene-summary">模型不是被瞬时切换，而是通过轨道激活、能量汇聚与节点校准逐步接入当前空间。</p>
      </div>

      <div class="span-4 loading-core">
        <OrbitLoading :progress="view.progressRatio" :loaded="state.runtime.loaded" :caption="state.runtime.progressMessage" label="加载轨道" />
      </div>

      <div class="span-4 scene-side-stack">
        <HoloCard class="loading-readout-card" tone="strong">
          <p class="scene-kicker">当前核心</p>
          <h2 class="metric-display">{{ view.currentModelName }}</h2>
          <MetricLine label="整体进度" :value="`${view.progressPercent}%`" :progress="view.progressRatio" />
          <MetricLine label="当前状态" :value="view.stateLabel" :progress="view.progressRatio" />
        </HoloCard>
      </div>

      <div class="span-12">
        <HoloCard class="step-card">
          <div v-for="step in view.loadingSteps" :key="step.label" class="step-row" :class="{ 'is-active': step.active, 'is-done': step.done }">
            <span class="step-row__dot" aria-hidden="true"></span>
            <span>{{ step.label }}</span>
            <strong>{{ step.done ? "完成" : step.active ? "进行中" : "等待" }}</strong>
          </div>
        </HoloCard>
      </div>

      <div class="span-12 action-row action-row--loading">
        <ActionButton label="返回工作台" subtitle="Workbench" :icon-path="ICON_PATHS.workbench" semantic="model" @click="actions.navigate('workbench')" />
        <ActionButton label="开始对话" subtitle="Chat Space" :icon-path="ICON_PATHS.chat" semantic="chat" @click="actions.beginConversation" />
      </div>
    </div>
  </section>
</template>
