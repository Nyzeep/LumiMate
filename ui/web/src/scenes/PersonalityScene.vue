<script setup>
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
  <section class="scene-panel scene-panel--personality" :class="{ 'is-active': active }" aria-label="个性化">
    <div class="scene-ambient scene-ambient--personality" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-5 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">温柔</h2>
        <p class="scene-summary">把 Lumi 的情绪底色、存在强度和呼吸频率重新整理成一张完整而克制的人格剖面。</p>
        <div class="mode-pills">
          <button type="button" :class="{ 'is-active': state.emotion.mood === 'quiet' }" @click.prevent="actions.setMood('quiet')">静谧</button>
          <button type="button" :class="{ 'is-active': state.emotion.mood === 'present' }" @click.prevent="actions.setMood('present')">在场</button>
          <button type="button" :class="{ 'is-active': state.emotion.mood === 'thinking' }" @click.prevent="actions.setMood('thinking')">思索</button>
        </div>
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
