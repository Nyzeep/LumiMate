<script setup>
import { computed } from "vue";
import GlassControl from "./GlassControl.vue";

const props = defineProps({
  task: {
    type: Object,
    default: null
  },
  stateLabel: {
    type: String,
    default: ""
  }
});

const emit = defineEmits(["plan-decision", "permission-decision", "pause", "resume", "cancel"]);

const primaryCommand = computed(() => {
  const task = props.task;
  if (!task) {
    return null;
  }
  if (task.state === "awaiting_permission" && task.permission) {
    return {
      event: "permission-decision",
      value: true,
      label: "允许",
      subtitle: "Allow",
      caption: "确认 " + (task.permission.category || "当前") + " 权限"
    };
  }
  if (task.state === "awaiting_plan_approval") {
    return { event: "plan-decision", value: true, label: "确认计划", subtitle: "Approve", caption: "确认后才会开始受控执行" };
  }
  if (task.state === "running") {
    return { event: "pause", label: "暂停任务", subtitle: "Pause", caption: "保留当前上下文并暂停下一步" };
  }
  if (task.state === "paused") {
    return { event: "resume", label: "恢复任务", subtitle: "Resume", caption: "从已保存的上下文继续" };
  }
  return null;
});

const statusCaption = computed(() => {
  if (props.task?.state === "awaiting_permission" && !props.task.permission) {
    return "权限请求详情正在恢复";
  }
  return primaryCommand.value?.caption || props.stateLabel || "等待任务状态";
});

const dangerCommand = computed(() => {
  const task = props.task;
  if (!task) {
    return null;
  }
  if (task.state === "awaiting_permission" && task.permission) {
    return { event: "permission-decision", value: false, label: "拒绝权限", subtitle: "Reject", caption: "拒绝当前权限请求" };
  }
  if (task.state === "awaiting_plan_approval") {
    return { event: "plan-decision", value: false, label: "拒绝计划", subtitle: "Reject", caption: "拒绝后不会开始任务" };
  }
  if (task.state === "awaiting_permission") {
    return { event: "cancel", label: "取消任务", subtitle: "Cancel", caption: "权限详情正在恢复时仍可安全取消任务" };
  }
  if (["draft", "planning", "running", "paused"].includes(task.state)) {
    return { event: "cancel", label: "取消任务", subtitle: "Cancel", caption: "取消会结束当前受控任务" };
  }
  return null;
});

function trigger(command) {
  if (!command) {
    return;
  }
  if ("value" in command) {
    emit(command.event, command.value);
  } else {
    emit(command.event);
  }
}
</script>

<template>
  <section class="task-command-rail" aria-label="任务命令">
    <div class="task-command-rail__context">
      <p class="scene-kicker">当前命令</p>
      <strong>{{ statusCaption }}</strong>
      <small>{{ stateLabel }}</small>
    </div>

    <GlassControl
      v-if="primaryCommand"
      class="task-command-rail__primary"
      kind="compact"
      priority="primary"
      accent="model"
      :label="primaryCommand.label"
      :subtitle="primaryCommand.subtitle"
      @click="trigger(primaryCommand)"
    />

    <section v-if="dangerCommand" class="task-command-rail__danger-zone" aria-label="危险操作区">
      <div>
        <p class="scene-kicker">危险操作</p>
        <small>{{ dangerCommand.caption }}</small>
      </div>
      <GlassControl
        kind="compact"
        priority="quiet"
        intent="danger"
        :label="dangerCommand.label"
        :subtitle="dangerCommand.subtitle"
        @click="trigger(dangerCommand)"
      />
    </section>
  </section>
</template>

<style scoped>
.task-command-rail {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 14px;
  border: var(--border-hairline) solid rgba(255, 208, 162, 0.2);
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.065), rgba(255, 182, 118, 0.045));
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.12), 0 12px 30px rgba(0, 0, 0, 0.16);
}

.task-command-rail__context {
  display: grid;
  gap: 4px;
}

.task-command-rail__context strong {
  font-size: var(--text-body);
  font-weight: 400;
}

.task-command-rail__context small,
.task-command-rail__danger-zone small {
  color: var(--color-dim);
  font-family: var(--font-mono);
  font-size: var(--text-status);
  letter-spacing: var(--tracking-mono);
}

.task-command-rail__primary {
  min-width: 148px;
}

.task-command-rail__danger-zone {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 10px;
  border-top: var(--border-hairline) solid rgba(229, 169, 127, 0.3);
}

.task-command-rail__danger-zone > div {
  display: grid;
  gap: 3px;
}

@media (max-width: 680px) {
  .task-command-rail,
  .task-command-rail__danger-zone {
    grid-template-columns: 1fr;
  }

  .task-command-rail__danger-zone {
    display: grid;
  }

  .task-command-rail :deep(.glass-control) {
    width: 100%;
  }
}
</style>
