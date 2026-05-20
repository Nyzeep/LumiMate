<script setup>
import { computed, reactive, watch } from "vue";
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

const local = reactive({
  subspace: "core",
  providerByKind: {
    asr: "modelscope",
    llm: "modelscope"
  }
});

const awakening = computed(() =>
  ["loading_asr", "loading_llm", "loading_tts", "switching", "validating"].includes(props.state.runtime.state)
);

const componentStatus = computed(() => props.state.runtime.componentStatus);
const missingRequired = computed(() => componentStatus.value.missingRequired || []);
const shouldOpenGalaxy = computed(() => props.active && missingRequired.value.length > 0);
const downloadBusy = computed(() => ["scanning", "downloading", "organizing"].includes(props.state.runtime.downloadState));
const downloadProgressRatio = computed(() => Math.max(0, Math.min(1, Number(props.state.runtime.downloadProgress || 0) / 100)));

watch(
  shouldOpenGalaxy,
  async (value) => {
    if (!value) {
      return;
    }
    local.subspace = "galaxy";
    await props.actions.openModelGalaxy?.();
  },
  { immediate: true }
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

function setSubspace(value) {
  local.subspace = value;
  if (value === "galaxy") {
    void props.actions.openModelGalaxy?.();
  }
}

function providerLabel(provider) {
  return provider === "huggingface" ? "Hugging Face" : "魔搭社区";
}

function modelIdFor(item, kind) {
  const provider = local.providerByKind[kind] || "modelscope";
  return item.providers?.[provider] || "";
}

async function startDownload(kind, item) {
  const provider = local.providerByKind[kind] || "modelscope";
  const modelId = modelIdFor(item, kind);
  if (!modelId || item.placeholder) {
    return;
  }
  await props.actions.startModelDownload?.(kind, provider, modelId, item.title);
}
</script>

<template>
  <section
    class="scene-panel scene-panel--workbench"
    :class="{ 'is-active': active, 'is-awakening': awakening, 'is-loaded': state.runtime.loaded, 'is-galaxy': local.subspace === 'galaxy' }"
    aria-label="工作台"
  >
    <div class="scene-ambient scene-ambient--workbench" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-12 workbench-subspace-switch">
        <button type="button" :class="{ 'is-active': local.subspace === 'core' }" @click.prevent="setSubspace('core')">
          <span>核心舱</span>
          <small>Core Chamber</small>
        </button>
        <button type="button" :class="{ 'is-active': local.subspace === 'galaxy' }" @click.prevent="setSubspace('galaxy')">
          <span>星系选择</span>
          <small>Model Galaxy</small>
        </button>
      </div>

      <template v-if="local.subspace === 'core'">
        <div class="span-4 scene-copy">
          <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
          <h2 class="scene-heading scene-heading--medium">模型编排</h2>
          <p class="scene-summary">这里围绕节点身份、状态、标签与激活过程组织模型系统，让 Lumi 的核心能力以更安静的方式被唤醒。</p>
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

        <div class="span-12 model-grid workbench-core-grid">
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

        <div class="span-12 action-row action-row--wide action-row--workbench">
          <ActionButton label="扫描节点" subtitle="Scan" :icon-path="ICON_PATHS.scan" semantic="model" @click="actions.scanComponents" />
          <ActionButton label="星系选择" subtitle="Galaxy" :icon-path="ICON_PATHS.workbench" semantic="model" @click="setSubspace('galaxy')" />
          <ActionButton label="加载模型" subtitle="Load" :icon-path="ICON_PATHS.load" tier="primary" semantic="model" @click="actions.loadModels" />
          <ActionButton label="切换核心" subtitle="Switch" :icon-path="ICON_PATHS.switch" semantic="model" @click="actions.switchModels" />
          <ActionButton label="释放缓存" subtitle="Release" :icon-path="ICON_PATHS.release" semantic="system" @click="actions.releaseCache" />
        </div>
      </template>

      <template v-else>
        <div class="span-4 scene-copy">
          <TechText as="p" tone="muted">MODEL GALAXY / 星系选择</TechText>
          <h2 class="scene-heading scene-heading--medium">为 Lumi 选择星系</h2>
          <p class="scene-summary">首次启动时，Lumi 会扫描本地模型组件。缺失的 ASR 或 LLM 可以在这里从魔搭社区或 Hugging Face 下载，并自动归档到对应目录。</p>
        </div>

        <div class="span-4 workbench-core">
          <OrbitLoading :progress="downloadProgressRatio" :loaded="state.runtime.downloadState === 'complete'" :caption="state.runtime.downloadMessage" label="模型星图扫描" />
        </div>

        <div class="span-4 scene-side-stack">
          <HoloCard class="info-card" tone="strong">
            <p class="scene-kicker">组件扫描</p>
            <div class="component-status-list">
              <div v-for="node in [componentStatus.asr, componentStatus.llm, componentStatus.tts]" :key="node.kind" class="component-status" :class="`is-${node.status}`">
                <strong>{{ node.label }}</strong>
                <small>{{ node.ready ? `${node.count} 个本地节点` : node.note }}</small>
              </div>
            </div>
          </HoloCard>
        </div>

        <div class="span-12 galaxy-scroll">
          <div class="galaxy-grid">
          <HoloCard class="galaxy-card galaxy-card--asr">
            <div class="galaxy-card__header">
              <div>
                <p class="scene-kicker">听觉星系 / ASR</p>
                <strong>{{ componentStatus.asr.ready ? "已检测到听觉节点" : "选择一个听觉节点" }}</strong>
              </div>
              <div class="provider-switch">
                <button type="button" :class="{ 'is-active': local.providerByKind.asr === 'modelscope' }" @click.prevent="local.providerByKind.asr = 'modelscope'">魔搭</button>
                <button type="button" :class="{ 'is-active': local.providerByKind.asr === 'huggingface' }" @click.prevent="local.providerByKind.asr = 'huggingface'">HF</button>
              </div>
            </div>
            <div class="download-card-list">
              <button
                v-for="item in state.runtime.downloadCatalog.asr"
                :key="item.id"
                type="button"
                class="download-card"
                :disabled="downloadBusy || !modelIdFor(item, 'asr')"
                @click.prevent="startDownload('asr', item)"
              >
                <span class="download-card__orbit" aria-hidden="true"></span>
                <strong>{{ item.title }}</strong>
                <small>{{ item.subtitle }}</small>
                <em>{{ providerLabel(local.providerByKind.asr) }} / {{ item.sizeLabel }}</em>
              </button>
            </div>
          </HoloCard>

          <HoloCard class="galaxy-card galaxy-card--llm">
            <div class="galaxy-card__header">
              <div>
                <p class="scene-kicker">思维星系 / LLM</p>
                <strong>{{ componentStatus.llm.ready ? "已检测到思维核心" : "选择一个思维核心" }}</strong>
              </div>
              <div class="provider-switch">
                <button type="button" :class="{ 'is-active': local.providerByKind.llm === 'modelscope' }" @click.prevent="local.providerByKind.llm = 'modelscope'">魔搭</button>
                <button type="button" :class="{ 'is-active': local.providerByKind.llm === 'huggingface' }" @click.prevent="local.providerByKind.llm = 'huggingface'">HF</button>
              </div>
            </div>
            <div class="download-card-list">
              <button
                v-for="item in state.runtime.downloadCatalog.llm"
                :key="item.id"
                type="button"
                class="download-card"
                :disabled="downloadBusy || !modelIdFor(item, 'llm')"
                @click.prevent="startDownload('llm', item)"
              >
                <span class="download-card__orbit" aria-hidden="true"></span>
                <strong>{{ item.title }}</strong>
                <small>{{ item.subtitle }}</small>
                <em>{{ providerLabel(local.providerByKind.llm) }} / {{ item.sizeLabel }}</em>
              </button>
            </div>
          </HoloCard>

          <HoloCard class="galaxy-card galaxy-card--tts">
            <div class="galaxy-card__header">
              <div>
                <p class="scene-kicker">声线星系 / TTS</p>
                <strong>{{ componentStatus.tts.ready ? "已检测到声线节点" : "声线加载即将开放" }}</strong>
              </div>
            </div>
            <div class="tts-placeholder">
              <span aria-hidden="true"></span>
              <p>{{ componentStatus.tts.note }}</p>
              <small>当前版本会继续扫描本地 `models/tts_model/`，远程下载和自定义导入会在后续接入。</small>
            </div>
          </HoloCard>
          </div>
        </div>

        <div class="span-12 download-console">
          <div class="download-console__bar">
            <span :style="{ transform: `scaleX(${downloadProgressRatio})` }"></span>
          </div>
          <div class="download-console__body">
            <strong>{{ state.runtime.downloadMessage }}</strong>
            <small>{{ state.runtime.downloadProgress }}%</small>
          </div>
          <div class="download-console__logs" v-if="state.runtime.downloadLogs.length">
            <p v-for="(log, index) in state.runtime.downloadLogs" :key="index">{{ log }}</p>
          </div>
        </div>

        <div class="span-12 action-row action-row--wide action-row--workbench action-row--galaxy">
          <ActionButton label="重新扫描" subtitle="Scan" :icon-path="ICON_PATHS.scan" semantic="model" @click="actions.scanComponents" />
          <ActionButton label="返回核心舱" subtitle="Core" :icon-path="ICON_PATHS.workbench" semantic="model" @click="setSubspace('core')" />
          <ActionButton
            v-if="downloadBusy"
            label="取消下载"
            subtitle="Cancel"
            :icon-path="ICON_PATHS.release"
            semantic="system"
            @click="actions.cancelModelDownload"
          />
        </div>
      </template>
    </div>
  </section>
</template>
