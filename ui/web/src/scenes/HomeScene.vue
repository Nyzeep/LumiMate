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
  <section class="scene-panel scene-panel--home" :class="{ 'is-active': active }" aria-label="首页">
    <div class="scene-ambient scene-ambient--home" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-4 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h1 class="scene-heading">晚上好</h1>
        <p class="scene-summary">{{ view.presenceCopy }}</p>

        <HoloCard class="info-card" tone="strong">
          <p class="scene-kicker">空间亮度</p>
          <MetricLine label="存在密度" :value="`${view.presencePercent}%`" :progress="state.emotion.presenceLevel" />
          <MetricLine label="呼吸节律" :value="`${view.breathPercent}%`" :progress="state.emotion.breathLevel" />
          <MetricLine label="环境模式" :value="view.ambientModeLabel" :progress="state.emotion.presenceLevel" />
          <p class="panel-note">由当前运行状态驱动的空间亮度与回应意愿。</p>
        </HoloCard>
      </div>

      <div class="span-5 hero-shell">
        <OrbitLoading :progress="view.progressRatio" :loaded="view.conversationReady" :caption="view.stateLabel" label="Lumi 中央核心" />
        <ActionButton
          class="hero-cta"
          :label="view.entryLabel"
          :subtitle="view.entryCaption"
          :icon-path="ICON_PATHS.home"
          tier="primary"
          semantic="core"
          block
          @click="actions.beginConversation"
        />
      </div>

      <div class="span-3 scene-side-stack">
        <HoloCard class="info-card">
          <p class="scene-kicker">当前状态</p>
          <MetricLine label="核心状态" :value="view.stateLabel" :progress="view.progressRatio" />
          <MetricLine label="回应意愿" :value="view.chatStageLabel" :progress="state.emotion.presenceLevel" />
          <MetricLine label="声线活性" :value="`${view.voicePercent}%`" :progress="state.chat.voiceLevel" />
        </HoloCard>

        <HoloCard class="info-card">
          <p class="scene-kicker">静默入口</p>
          <p class="panel-note">聊天、陪伴与工作台围绕同一颗核心切换，入口彼此让位，不争夺视线。</p>
        </HoloCard>
      </div>

      <div class="span-12 action-row action-row--home">
        <ActionButton
          label="陪伴空间"
          subtitle="Companion Space"
          :icon-path="ICON_PATHS.companion"
          tier="quiet"
          semantic="companion"
          truncate-copy
          @click="actions.navigate('companion')"
        />
        <ActionButton label="工作台" subtitle="Workbench" :icon-path="ICON_PATHS.workbench" tier="quiet" semantic="model" truncate-copy @click="actions.navigate('workbench')" />
      </div>
    </div>
  </section>
</template>
