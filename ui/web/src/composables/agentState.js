// Agent 事件纯归约：把 §8 agent.* 事件投影为任务舱 UI 状态。
// 不依赖 DOM / 网络 / Vue，可被 Node 直接验证。

function emptyTask(taskId) {
  return {
    taskId,
    title: "",
    state: "draft",
    plan: [],
    tools: [],
    fileChanges: [],
    testResults: [],
    permission: null,
    result: null,
    failure: null
  };
}

export function createAgentState() {
  return {
    ready: false,
    harnessAvailable: false,
    currentTask: null,
    sessions: [],
    memoryProposals: []
  };
}

function ensureTask(state, taskId) {
  if (state.currentTask && state.currentTask.taskId === taskId) {
    return state.currentTask;
  }
  const task = emptyTask(taskId);
  state.currentTask = task;
  return task;
}

function setState(state, event, value) {
  const task = ensureTask(state, event.taskId);
  task.state = value;
}

export function reduceAgentEvent(state, event) {
  const type = String(event.type || "");
  if (!type.startsWith("agent.")) {
    return state;
  }
  switch (type) {
    case "agent.task.created": {
      const task = ensureTask(state, event.taskId);
      task.title = event.title || task.title;
      task.state = event.state || task.state;
      break;
    }
    case "agent.task.planning":
      setState(state, event, "planning");
      break;
    case "agent.task.awaiting_plan_approval": {
      setState(state, event, "awaiting_plan_approval");
      const task = ensureTask(state, event.taskId);
      task.plan = Array.isArray(event.plan) ? event.plan : [];
      break;
    }
    case "agent.task.running":
      setState(state, event, "running");
      break;
    case "agent.task.awaiting_permission": {
      setState(state, event, "awaiting_permission");
      const task = ensureTask(state, event.taskId);
      task.permission = {
        requestId: event.requestId || "",
        category: event.category || "",
        toolName: event.toolName || "",
        details: event.details || {}
      };
      break;
    }
    case "agent.task.tool_started": {
      const task = ensureTask(state, event.taskId);
      task.tools.push({
        callId: event.callId || "",
        toolName: event.toolName || "",
        status: "running"
      });
      break;
    }
    case "agent.task.tool_finished": {
      const task = ensureTask(state, event.taskId);
      const entry = task.tools.find((tool) => tool.callId === event.callId);
      if (entry) {
        entry.status = event.status === "error" ? "error" : "ok";
      }
      break;
    }
    case "agent.task.file_changed": {
      const task = ensureTask(state, event.taskId);
      task.fileChanges.unshift({
        path: event.path || "",
        operation: event.operation || "",
        beforeHash: event.beforeHash || null,
        afterHash: event.afterHash || null
      });
      break;
    }
    case "agent.task.test_result": {
      const task = ensureTask(state, event.taskId);
      task.testResults.unshift({
        command: event.command || "",
        passed: Number(event.passed || 0),
        failed: Number(event.failed || 0),
        durationMs: Number(event.durationMs || 0)
      });
      break;
    }
    case "agent.task.paused":
      setState(state, event, "paused");
      break;
    case "agent.task.cancelled":
      setState(state, event, "cancelled");
      ensureTask(state, event.taskId).permission = null;
      break;
    case "agent.task.completed": {
      setState(state, event, "completed");
      const task = ensureTask(state, event.taskId);
      task.result = event.result || {};
      task.permission = null;
      break;
    }
    case "agent.task.failed": {
      setState(state, event, "failed");
      const task = ensureTask(state, event.taskId);
      task.failure = event.failure || { reason: "error" };
      task.permission = null;
      break;
    }
    case "agent.session.updated": {
      const session = {
        sessionId: event.sessionId || "",
        taskId: event.taskId || null,
        status: event.status || "",
        summary: event.summary || ""
      };
      const index = state.sessions.findIndex(
        (item) => item.sessionId === session.sessionId
      );
      if (index >= 0) {
        state.sessions[index] = session;
      } else {
        state.sessions.unshift(session);
      }
      break;
    }
    case "agent.memory.proposed":
      state.memoryProposals.unshift({
        proposalId: event.proposalId || "",
        summary: event.summary || "",
        kind: event.kind || ""
      });
      break;
    default:
      break;
  }
  return state;
}

export function applyAgentSnapshot(state, snapshot) {
  if (!snapshot || typeof snapshot !== "object") {
    return state;
  }
  state.ready = Boolean(snapshot.ready);
  state.harnessAvailable = Boolean(snapshot.harnessAvailable);
  if (snapshot.currentTask && typeof snapshot.currentTask === "object") {
    const task = snapshot.currentTask;
    state.currentTask = {
      ...emptyTask(task.taskId || ""),
      title: task.title || "",
      state: task.state || "draft",
      plan: Array.isArray(task.plan) ? task.plan : [],
      result: task.result || null,
      failure: task.failure || null
    };
  } else {
    state.currentTask = null;
  }
  state.sessions = Array.isArray(snapshot.sessions)
    ? snapshot.sessions.map((session) => ({
        sessionId: session.sessionId || "",
        taskId: session.taskId || null,
        status: session.status || "",
        summary: session.summary || ""
      }))
    : [];
  return state;
}
