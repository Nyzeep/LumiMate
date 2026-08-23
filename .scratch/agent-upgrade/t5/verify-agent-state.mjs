// T5 开发验证：纯 reducer 三态/事件归约断言（不进白名单）。
import assert from "node:assert/strict";
import {
  applyAgentSnapshot,
  createAgentState,
  reduceAgentEvent
} from "../../../ui/web/src/composables/agentState.js";

// 1. 空态
const empty = createAgentState();
assert.equal(empty.currentTask, null);
assert.deepEqual(empty.sessions, []);

// 2. 生命周期：created → planning → awaiting_plan_approval
const lifecycle = createAgentState();
reduceAgentEvent(lifecycle, {
  type: "agent.task.created",
  taskId: "t1",
  title: "修复测试",
  state: "draft"
});
reduceAgentEvent(lifecycle, { type: "agent.task.planning", taskId: "t1" });
reduceAgentEvent(lifecycle, {
  type: "agent.task.awaiting_plan_approval",
  taskId: "t1",
  plan: [{ summary: "计划" }]
});
assert.equal(lifecycle.currentTask.state, "awaiting_plan_approval");
assert.deepEqual(lifecycle.currentTask.plan, [{ summary: "计划" }]);
assert.equal(lifecycle.currentTask.title, "修复测试");

// 3. running + 工具/文件/测试事件
const run = createAgentState();
reduceAgentEvent(run, { type: "agent.task.running", taskId: "t1" });
reduceAgentEvent(run, {
  type: "agent.task.tool_started",
  taskId: "t1",
  callId: "c1",
  toolName: "write"
});
reduceAgentEvent(run, {
  type: "agent.task.tool_finished",
  taskId: "t1",
  callId: "c1",
  status: "ok"
});
reduceAgentEvent(run, {
  type: "agent.task.file_changed",
  taskId: "t1",
  path: "a.py",
  operation: "create",
  afterHash: "abc"
});
reduceAgentEvent(run, {
  type: "agent.task.test_result",
  taskId: "t1",
  command: "pytest",
  passed: 3,
  failed: 1,
  durationMs: 1230
});
assert.equal(run.currentTask.state, "running");
assert.equal(run.currentTask.tools[0].status, "ok");
assert.equal(run.currentTask.fileChanges[0].operation, "create");
assert.equal(run.currentTask.testResults[0].passed, 3);

// 4. 权限等待与批准后终态
const permission = createAgentState();
reduceAgentEvent(permission, { type: "agent.task.running", taskId: "t1" });
reduceAgentEvent(permission, {
  type: "agent.task.awaiting_permission",
  taskId: "t1",
  requestId: "r1",
  category: "file_modify",
  toolName: "write"
});
assert.equal(permission.currentTask.state, "awaiting_permission");
assert.equal(permission.currentTask.permission.requestId, "r1");
reduceAgentEvent(permission, {
  type: "agent.task.completed",
  taskId: "t1",
  result: { filesChanged: 1 }
});
assert.equal(permission.currentTask.state, "completed");
assert.equal(permission.currentTask.permission, null);
assert.equal(permission.currentTask.result.filesChanged, 1);

// 5. 失败
const failed = createAgentState();
reduceAgentEvent(failed, { type: "agent.task.planning", taskId: "t1" });
reduceAgentEvent(failed, {
  type: "agent.task.failed",
  taskId: "t1",
  failure: { reason: "error" }
});
assert.equal(failed.currentTask.state, "failed");
assert.deepEqual(failed.currentTask.failure, { reason: "error" });

// 6. Session 投影 upsert
const sessions = createAgentState();
reduceAgentEvent(sessions, {
  type: "agent.session.updated",
  sessionId: "s1",
  taskId: "t1",
  status: "idle",
  summary: "完成"
});
reduceAgentEvent(sessions, {
  type: "agent.session.updated",
  sessionId: "s1",
  status: "running",
  summary: "续跑"
});
assert.equal(sessions.sessions.length, 1);
assert.equal(sessions.sessions[0].status, "running");

// 7. 快照应用
const snapshotState = createAgentState();
applyAgentSnapshot(snapshotState, {
  ready: true,
  harnessAvailable: true,
  currentTask: { taskId: "t9", title: "快照任务", state: "paused", plan: [] },
  sessions: [{ sessionId: "s9", status: "idle", summary: "旧" }]
});
assert.equal(snapshotState.currentTask.state, "paused");
assert.equal(snapshotState.sessions[0].sessionId, "s9");

// 8. 非 agent 事件忽略
const ignored = createAgentState();
reduceAgentEvent(ignored, { type: "state.patch", state: {} });
assert.equal(ignored.currentTask, null);

console.log("verify-agent-state: PASSED");
