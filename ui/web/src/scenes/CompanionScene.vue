<script setup>
import HoloCard from "../components/HoloCard.vue";
import MetricLine from "../components/MetricLine.vue";
import OrbitalIconButton from "../components/OrbitalIconButton.vue";
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
  <section class="scene-panel scene-panel--companion" :class="{ 'is-active': active }" aria-label="陪伴空间">
    <div class="scene-ambient scene-ambient--companion" aria-hidden="true">
      <svg class="portrait-halo" viewBox="0 0 520 520">
        <circle cx="260" cy="260" r="208" />
        <circle cx="260" cy="260" r="162" />
        <circle cx="260" cy="260" r="120" />
        <path d="M164 334C214 294 306 294 356 334" />
      </svg>
    </div>

    <div class="scene-grid">
      <div class="span-4 companion-stage-shell">
        <div class="companion-stage">
          <div class="companion-stage__core">
            <span class="companion-stage__star"></span>
          </div>
        </div>
      </div>

      <div class="span-4 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">平静</h2>
        <p class="scene-summary">透明几何只负责环境反馈，不再遮挡人物本身。陪伴信息与操作收束到结构化的左侧与底部。</p>

        <HoloCard class="info-card">
          <p class="scene-kicker">舞台能力</p>
          <p class="panel-note">{{ state.companion.rendererType }}</p>
          <p class="panel-note">{{ state.companion.rendererCapability }}</p>
          <MetricLine label="存在亮度" :value="`${view.presencePercent}%`" :progress="state.emotion.presenceLevel" />
          <MetricLine label="语音脉冲" :value="`${Math.round(state.companion.speechLevel * 100)}%`" :progress="state.companion.speechLevel" />
        </HoloCard>
      </div>

      <div class="span-8 companion-tools-shell">
        <HoloCard class="info-card" tone="strong">
          <p class="scene-kicker">陪伴侧栏</p>
          <div class="companion-tools">
            <OrbitalIconButton label="回到核心" :icon-path="ICON_PATHS.memory" semantic="companion" @click="actions.navigate('home')" />
            <OrbitalIconButton label="人格空间" :icon-path="ICON_PATHS.mood" semantic="companion" @click="actions.navigate('personality')" />
            <OrbitalIconButton label="对话记录" :icon-path="ICON_PATHS.chat" semantic="chat" @click="actions.navigate('chat')" />
            <OrbitalIconButton label="存储概览" :icon-path="ICON_PATHS.storage" semantic="system" @click="actions.navigate('storage')" />
          </div>
          <MetricLine label="情绪安稳度" :value="view.moodLabel" :progress="state.emotion.presenceLevel" />
        </HoloCard>
      </div>
    </div>
  </section>
</template>
