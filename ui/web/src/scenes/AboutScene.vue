<script setup>
import HoloCard from "../components/HoloCard.vue";
import TechText from "../components/TechText.vue";

const props = defineProps({
  scene: { type: Object, required: true },
  active: { type: Boolean, default: false },
  state: { type: Object, required: true },
  view: { type: Object, required: true },
  actions: { type: Object, required: true }
});

function basename(value) {
  const normalized = String(value || "").replace(/\\/g, "/");
  return normalized.split("/").filter(Boolean).pop() || normalized || "-";
}

function workspaceLabel() {
  return basename(props.state.app.projectRoot) || "LumiMate";
}

function pythonLabel() {
  return basename(props.state.app.pythonExecutable) || "python";
}

function authorName() {
  return props.state.app.appAuthor || "Nyzeep";
}
</script>

<template>
  <section class="scene-panel scene-panel--about" :class="{ 'is-active': active }" aria-label="关于 Lumi">
    <div class="scene-ambient scene-ambient--about" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-5 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">LumiMate</h2>
        <p class="scene-summary">数字陪伴空间不只是一层工具界面，而是一处可停留、可呼吸、可回应的意识场。</p>
      </div>

      <div class="span-7 about-metrics">
        <HoloCard class="about-card">
          <div class="about-card__hero">
            <div class="about-avatar-shell">
              <img class="about-avatar" :src="state.app.authorAvatarUrl" :alt="`${authorName()} avatar`" />
            </div>
            <div class="about-card__identity">
              <span>作者</span>
              <strong>{{ authorName() }}</strong>
              <p>以安静、秩序与陪伴感构建 LumiMate 的空间体验。</p>
            </div>
          </div>

          <div class="about-card__row"><span>版本</span><strong>{{ state.app.appVersion || "0.1.0" }}</strong></div>
          <div class="about-card__row"><span>作者</span><strong>{{ authorName() }}</strong></div>
          <div class="about-card__row"><span>项目地址</span><strong class="about-card__mono">{{ state.app.projectUrl || "https://github.com/Nyzeep/LumiMate" }}</strong></div>
          <div class="about-card__row"><span>工作区</span><strong>{{ workspaceLabel() }}</strong></div>
          <div class="about-card__row"><span>解释器</span><strong>{{ pythonLabel() }}</strong></div>
        </HoloCard>
      </div>
    </div>
  </section>
</template>
