<script setup>
import ControlGroup from "../components/ControlGroup.vue";
import HoloCard from "../components/HoloCard.vue";
import MetricLine from "../components/MetricLine.vue";
import OrbitLoading from "../components/OrbitLoading.vue";
import TechText from "../components/TechText.vue";

const moods = [
  { id: "quiet", label: "静谧" },
  { id: "present", label: "在场" },
  { id: "thinking", label: "思索" }
];

defineProps({
  scene: { type: Object, required: true },
  active: { type: Boolean, default: false },
  state: { type: Object, required: true },
  view: { type: Object, required: true },
  actions: { type: Object, required: true }
});
</script>

<template>
  <section class="scene-panel scene-panel--personality" :class="{ 'is-active': active }" aria-label="个性化">
    <div class="scene-ambient scene-ambient--personality" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-5 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">温柔</h2>
        <p class="scene-summary">把 Lumi 的情绪底色、存在强度和呼吸频率重新整理成一张完整而克制的人格剖面。</p>
        <ControlGroup
          class="mode-pills"
          :items="moods"
          :selected-id="state.emotion.mood"
          selection-role="radio"
          accent="companion"
          aria-label="人格情绪"
          @select="actions.setMood"
        />
        <HoloCard class="info-card">
          <MetricLine label="情绪共鸣强度" :value="`${view.presencePercent}%`" :progress="state.emotion.presenceLevel" />
          <MetricLine label="呼吸节律" :value="`${view.breathPercent}%`" :progress="state.emotion.breathLevel" />
        </HoloCard>
      </div>

      <div class="span-4">
        <OrbitLoading :progress="state.emotion.presenceLevel" :loaded="state.emotion.presenceLevel > 0.5" caption="Personality" label="人格轨道" />
      </div>

      <div class="span-3">
        <HoloCard class="info-card" tone="strong">
          <p class="scene-kicker">当前人格</p>
          <p class="panel-note">情绪：{{ view.moodLabel }}</p>
          <p class="panel-note">存在：{{ view.stateLabel }}</p>
          <p class="panel-note">倾听：{{ state.emotion.isListening ? "正在进行" : "尚未开始" }}</p>
        </HoloCard>
      </div>
    </div>
  </section>
</template>
