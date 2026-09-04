<script setup>
import { computed, reactive, watch } from "vue";
import ActionButton from "../components/ActionButton.vue";
import ControlGroup from "../components/ControlGroup.vue";
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

const subspaces = [
  { id: "core", label: "核心舱", subtitle: "Core Chamber" },
  { id: "galaxy", label: "星系选择", subtitle: "Model Galaxy" },
  { id: "agent", label: "任务舱", subtitle: "Task Chamber" }
];

const local = reactive({
  subspace: "core",
  agentTitle: "",
  agentGoal: "",
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

function agentStateLabel(value) {
  const labels = {
    draft: "草稿",
    planning: "规划中",
    awaiting_plan_approval: "等待计划确认",
    awaiting_permission: "等待权限",
    running: "运行中",
    paused: "已暂停",
    cancelling: "取消中",
    cancelled: "已取消",
    completed: "已完成",
    failed: "失败"
  };
  return labels[value] || value || "未知";
}

async function startAgentTask() {
  const title = local.agentTitle.trim();
  const goal = local.agentGoal.trim();
  if (!title || !goal) {
    return;
  }
  await props.actions.agentStartTask?.(title, goal);
}

async function approvePlan(approve) {
  const task = props.state.agent.currentTask;
  if (task) {
    await props.actions.agentApprovePlan?.(task.taskId, approve);
  }
}

async function approvePermission(approve) {
  const task = props.state.agent.currentTask;
  const permission = task?.permission;
  if (task && permission) {
    await props.actions.agentApprovePermission?.(task.taskId, permission.requestId, permission.category, approve);
  }
}

async function pauseTask() {
  const task = props.state.agent.currentTask;
  if (task) {
    await props.actions.agentPauseTask?.(task.taskId);
  }
}

async function resumeTask() {
  const task = props.state.agent.currentTask;
  if (task) {
    await props.actions.agentResumeTask?.(task.taskId);
  }
}

async function cancelTask() {
  const task = props.state.agent.currentTask;
  if (task) {
    await props.actions.agentCancelTask?.(task.taskId);
  }
}

async function resumeSession(sessionId) {
  const goal = local.agentGoal.trim() || "恢复任务";
  await props.actions.agentResumeSession?.(sessionId, goal);
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
      <ControlGroup
        class="span-12 workbench-subspace-switch"
        :items="subspaces"
        :selected-id="local.subspace"
        selection-role="radio"
        accent="model"
        aria-label="工作台子空间"
        @select="setSubspace"
      />

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
          <ActionButton label="释放缓存" subtitle="Release" :icon-path="ICON_PATHS.release" tier="quiet" intent="danger" semantic="system" @click="actions.releaseCache" />
        </div>
      </template>

      <template v-else-if="local.subspace === 'galaxy'">
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
            tier="quiet"
            intent="danger"
            semantic="system"
            @click="actions.cancelModelDownload"
          />
        </div>
      </template>
      <template v-else-if="local.subspace === 'agent'">
        <div class="span-4 scene-copy">
          <TechText as="p" tone="muted">TASK CHAMBER / 任务舱</TechText>
          <h2 class="scene-heading scene-heading--medium">受控任务</h2>
          <p class="scene-summary">让 Task Agent 在固定工作区内执行受控开发任务；计划与权限始终由你确认。</p>
          <div class="agent-start-form">
            <input v-model="local.agentTitle" class="agent-input" placeholder="任务标题" />
            <textarea v-model="local.agentGoal" class="agent-input" rows="3" placeholder="任务目标（例如：让 pytest 全绿）"></textarea>
            <ActionButton label="发起任务" subtitle="Start" :icon-path="ICON_PATHS.workbench" tier="primary" semantic="model" @click="startAgentTask" />
          </div>
        </div>

        <div class="span-8 agent-panel">
          <HoloCard v-if="view.agent.currentTask" class="agent-task-card" tone="strong">
            <p class="scene-kicker">当前任务</p>
            <strong>{{ view.agent.currentTask.title }}</strong>
            <p class="agent-state">{{ agentStateLabel(view.agent.currentTask.state) }}</p>
            <ul v-if="view.agent.currentTask.plan.length" class="agent-plan-list">
              <li v-for="(step, index) in view.agent.currentTask.plan" :key="index">{{ step.summary || step }}</li>
            </ul>
            <div v-if="view.agent.currentTask.state === 'awaiting_plan_approval'" class="agent-permission-card">
              <p>计划待确认</p>
              <div class="action-row action-row--agent">
                <ActionButton label="确认计划" subtitle="Approve" tier="primary" semantic="model" @click="approvePlan(true)" />
                <ActionButton label="拒绝计划" subtitle="Reject" tier="quiet" intent="danger" semantic="system" @click="approvePlan(false)" />
              </div>
            </div>
            <div v-if="view.agent.currentTask.permission" class="agent-permission-card">
              <p>等待权限：{{ view.agent.currentTask.permission.category }}（{{ view.agent.currentTask.permission.toolName }}）</p>
              <div class="action-row action-row--agent">
                <ActionButton label="允许" subtitle="Allow" tier="primary" semantic="model" @click="approvePermission(true)" />
                <ActionButton label="拒绝" subtitle="Reject" tier="quiet" intent="danger" semantic="system" @click="approvePermission(false)" />
              </div>
            </div>
            <div v-if="view.agent.currentTask.failure" class="agent-failure-card">
              <p>失败原因：{{ view.agent.currentTask.failure.reason }}</p>
            </div>
            <div class="action-row action-row--agent">
              <ActionButton label="暂停" subtitle="Pause" semantic="system" @click="pauseTask" />
              <ActionButton label="恢复" subtitle="Resume" semantic="model" @click="resumeTask" />
              <ActionButton label="取消" subtitle="Cancel" tier="quiet" intent="danger" semantic="system" @click="cancelTask" />
            </div>
          </HoloCard>

          <HoloCard v-else class="agent-empty-card">
            <p class="scene-kicker">空态</p>
            <p class="scene-summary">让 Lumi 帮你做事——输入目标并发起第一个受控任务。</p>
          </HoloCard>

          <HoloCard v-if="view.agent.currentTask" class="agent-trail-card">
            <p class="scene-kicker">轨迹</p>
            <div class="agent-trail-grid">
              <div>
                <strong>工具</strong>
                <ul>
                  <li v-for="tool in view.agent.currentTask.tools.slice(-6).reverse()" :key="tool.callId">{{ tool.toolName }} · {{ tool.status }}</li>
                </ul>
              </div>
              <div>
                <strong>文件变更</strong>
                <ul>
                  <li v-for="change in view.agent.currentTask.fileChanges.slice(0, 6)" :key="change.path + change.afterHash">{{ change.operation }} {{ change.path }}</li>
                </ul>
              </div>
              <div>
                <strong>测试结果</strong>
                <ul>
                  <li v-for="test in view.agent.currentTask.testResults.slice(0, 6)" :key="test.command + test.durationMs">{{ test.command }} · {{ test.passed }} passed / {{ test.failed }} failed</li>
                </ul>
              </div>
            </div>
          </HoloCard>

          <HoloCard class="agent-sessions-card">
            <p class="scene-kicker">最近 Session</p>
            <button
              v-for="session in view.agent.sessions.slice(0, 5)"
              :key="session.sessionId"
              type="button"
              class="agent-session-row"
              @click.prevent="resumeSession(session.sessionId)"
            >
              <span>{{ session.sessionId }}</span>
              <small>{{ session.status }} · {{ session.summary }}</small>
            </button>
            <p v-if="!view.agent.sessions.length" class="panel-note">暂无历史 Session。</p>
          </HoloCard>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.agent-start-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.agent-input {
  width: 100%;
  box-sizing: border-box;
  background: rgba(10, 18, 30, 0.7);
  border: 1px solid rgba(247, 200, 115, 0.22);
  border-radius: 0.6rem;
  color: var(--text-primary, #e8e2d4);
  padding: 0.6rem 0.8rem;
  font: inherit;
}

.agent-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.agent-state {
  color: var(--accent-gold, #f7c873);
  font-size: 0.9rem;
  margin: 0.25rem 0 0.5rem;
}

.agent-plan-list,
.agent-trail-grid ul {
  margin: 0;
  padding-left: 1rem;
  color: var(--text-secondary, #b7ad9a);
  font-size: 0.85rem;
}

.agent-permission-card,
.agent-failure-card {
  margin: 0.75rem 0;
  padding: 0.75rem;
  border-radius: 0.6rem;
  background: rgba(247, 200, 115, 0.08);
  border: 1px solid rgba(247, 200, 115, 0.25);
}

.agent-failure-card {
  background: rgba(220, 90, 90, 0.08);
  border-color: rgba(220, 90, 90, 0.3);
}

.action-row--agent {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.agent-trail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.agent-trail-grid ul {
  list-style: none;
  padding-left: 0;
}

.agent-session-row {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  width: 100%;
  text-align: left;
  background: transparent;
  border: 1px solid rgba(247, 200, 115, 0.18);
  border-radius: 0.5rem;
  padding: 0.5rem 0.7rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary, #e8e2d4);
  cursor: pointer;
}

.agent-session-row small {
  color: var(--text-secondary, #b7ad9a);
}

@media (max-width: 900px) {
  .agent-trail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
