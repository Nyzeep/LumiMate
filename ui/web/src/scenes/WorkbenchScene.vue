<script setup>
import { computed } from "vue";
import ActionButton from "../components/ActionButton.vue";
import HoloCard from "../components/HoloCard.vue";
import OrbitLoading from "../components/OrbitLoading.vue";
import TechText from "../components/TechText.vue";
import { ICON_PATHS } from "../app/sceneRegistry";

const props = defineProps({
  scene: { type: Object, required: true },
  active: { type: Boolean, default: false },
  state: { type: Object, required: true },
  view: { type: Object, required: true },
  actions: { type: Object, required: true }
});

const awakening = computed(() =>
  ["loading_asr", "loading_llm", "loading_tts", "switching", "validating"].includes(props.state.runtime.state)
);

async function inspectNode(type, path) {
  if (path) {
    await props.actions.selectModel(type, path);
  }
  props.actions.openDrawer(type);
}

function modelStatusLabel(status) {
  const labels = {
    idle: "静置",
    ready: "就绪",
    selected: "已选",
    active: "激活",
    awakening: "苏醒中",
    empty: "缺失"
  };
  return labels[status] || status;
}
</script>

<template>
  <section
    class="scene-panel scene-panel--workbench"
    :class="{ 'is-active': active, 'is-awakening': awakening, 'is-loaded': state.runtime.loaded }"
    aria-label="工作台"
  >
    <div class="scene-ambient scene-ambient--workbench" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-4 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">模型编排</h2>
        <p class="scene-summary">这里不再暴露原始路径，而是围绕节点身份、状态、标签与激活过程组织模型系统。</p>
      </div>

      <div class="span-4 workbench-core">
        <OrbitLoading :progress="view.progressRatio" :loaded="state.runtime.loaded" :caption="view.stateLabel" label="工作台核心轨道" />
      </div>

      <div class="span-4 scene-side-stack">
        <HoloCard class="info-card" tone="strong">
          <p class="scene-kicker">运行低语</p>
          <p class="panel-note">{{ view.runtimeMessage }}</p>
          <ul class="log-list">
            <li v-for="(log, index) in view.shortLogs" :key="index">{{ log }}</li>
          </ul>
        </HoloCard>
      </div>

      <div class="span-12 model-grid">
        <HoloCard class="model-group-card">
          <div class="model-group-card__header">
            <strong>思维核心</strong>
            <small>{{ view.currentModelName }}</small>
          </div>
          <div class="model-card-list">
            <button
              v-for="entry in view.modelCatalog.llm"
              :key="entry.id"
              type="button"
              class="model-card"
              :class="[`is-${entry.status}`, { 'is-selected': entry.selected }]"
              data-promoted-layer="true"
              @click.prevent="inspectNode('llm', entry.path)"
            >
              <span class="model-card__status" aria-hidden="true"></span>
              <div class="model-card__content">
                <strong>{{ entry.title }}</strong>
                <small>{{ entry.subtitle }}</small>
              </div>
              <div class="model-card__meta">
                <em>{{ modelStatusLabel(entry.status) }}</em>
                <div class="model-card__tags">
                  <span v-for="tag in entry.tags" :key="tag">{{ tag }}</span>
                </div>
              </div>
            </button>
          </div>
        </HoloCard>

        <HoloCard class="model-group-card">
          <div class="model-group-card__header">
            <strong>听觉节点</strong>
            <small>{{ view.currentAsrName }}</small>
          </div>
          <div class="model-card-list">
            <button
              v-for="entry in view.modelCatalog.asr"
              :key="entry.id"
              type="button"
              class="model-card"
              :class="[`is-${entry.status}`, { 'is-selected': entry.selected }]"
              data-promoted-layer="true"
              @click.prevent="inspectNode('asr', entry.path)"
            >
              <span class="model-card__status" aria-hidden="true"></span>
              <div class="model-card__content">
                <strong>{{ entry.title }}</strong>
                <small>{{ entry.subtitle }}</small>
              </div>
              <div class="model-card__meta">
                <em>{{ modelStatusLabel(entry.status) }}</em>
                <div class="model-card__tags">
                  <span v-for="tag in entry.tags" :key="tag">{{ tag }}</span>
                </div>
              </div>
            </button>
          </div>
        </HoloCard>

        <HoloCard class="model-group-card">
          <div class="model-group-card__header">
            <strong>声线节点</strong>
            <small>{{ view.currentTtsName }}</small>
          </div>
          <div class="model-card-list">
            <button
              v-for="entry in view.modelCatalog.tts"
              :key="entry.id"
              type="button"
              class="model-card"
              :class="[`is-${entry.status}`, { 'is-selected': entry.selected }]"
              data-promoted-layer="true"
              @click.prevent="inspectNode('tts', entry.path)"
            >
              <span class="model-card__status" aria-hidden="true"></span>
              <div class="model-card__content">
                <strong>{{ entry.title }}</strong>
                <small>{{ entry.subtitle }}</small>
              </div>
              <div class="model-card__meta">
                <em>{{ modelStatusLabel(entry.status) }}</em>
                <div class="model-card__tags">
                  <span v-for="tag in entry.tags" :key="tag">{{ tag }}</span>
                </div>
              </div>
            </button>
          </div>
        </HoloCard>
      </div>

      <div class="span-12 action-row action-row--wide">
        <ActionButton label="扫描节点" subtitle="Scan" :icon-path="ICON_PATHS.scan" semantic="model" @click="actions.scanModels" />
        <ActionButton label="加载模型" subtitle="Load" :icon-path="ICON_PATHS.load" tier="primary" semantic="model" @click="actions.loadModels" />
        <ActionButton label="切换核心" subtitle="Switch" :icon-path="ICON_PATHS.switch" semantic="model" @click="actions.switchModels" />
        <ActionButton label="释放缓存" subtitle="Release" :icon-path="ICON_PATHS.release" semantic="system" @click="actions.releaseCache" />
      </div>
    </div>
  </section>
</template>
