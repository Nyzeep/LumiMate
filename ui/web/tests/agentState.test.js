// agentState 纯归约模块的 node:test 验证（无需 vitest/依赖，node --test 直接运行）。
import { test } from "node:test";
import assert from "node:assert/strict";

import {
  applyAgentSnapshot,
  createAgentState,
  reduceAgentEvent
} from "../src/composables/agentState.js";

function snapshotFor(task) {
  return {
    ready: true,
    harnessAvailable: true,
    currentTask: task,
    sessions: []
  };
}

function seedLiveTask(state, taskId = "t1") {
  reduceAgentEvent(state, {
    type: "agent.task.created",
    taskId,
    title: "修复测试",
    state: "planning"
  });
  reduceAgentEvent(state, {
    type: "agent.task.tool_started",
    taskId,
    toolName: "write",
    callId: "c1"
  });
  reduceAgentEvent(state, {
    type: "agent.task.awaiting_permission",
    taskId,
    requestId: "c1",
    category: "file_modify",
    toolName: "write",
    details: {}
  });
  return state;
}

test("同一 Task 的 HTTP 快照保留事件现场（permission/tools 不被轮询抹掉）", () => {
  const state = seedLiveTask(createAgentState());

  applyAgentSnapshot(
    state,
    snapshotFor({ taskId: "t1", title: "修复测试", state: "awaiting_permission" })
  );

  assert.equal(state.currentTask.state, "awaiting_permission");
  assert.equal(state.currentTask.permission.requestId, "c1");
  assert.equal(state.currentTask.tools.length, 1);
  assert.equal(state.currentTask.tools[0].status, "running");
  assert.deepEqual(state.currentTask.fileChanges, []);
  assert.deepEqual(state.currentTask.testResults, []);
});

test("快照权威字段（title/state/plan/result/failure）仍以快照为准", () => {
  const state = seedLiveTask(createAgentState());

  applyAgentSnapshot(
    state,
    snapshotFor({
      taskId: "t1",
      title: "新标题",
      state: "running",
      plan: [{ summary: "步骤" }],
      result: { filesChanged: 2 }
    })
  );

  assert.equal(state.currentTask.title, "新标题");
  assert.equal(state.currentTask.state, "running");
  assert.deepEqual(state.currentTask.plan, [{ summary: "步骤" }]);
  assert.deepEqual(state.currentTask.result, { filesChanged: 2 });
});

test("快照指向不同 Task 时整体替换，不携带旧任务现场", () => {
  const state = seedLiveTask(createAgentState());

  applyAgentSnapshot(
    state,
    snapshotFor({ taskId: "t2", title: "新任务", state: "running" })
  );

  assert.equal(state.currentTask.taskId, "t2");
  assert.deepEqual(state.currentTask.tools, []);
  assert.equal(state.currentTask.permission, null);
});

test("currentTask 为空时清空活任务", () => {
  const state = seedLiveTask(createAgentState());

  applyAgentSnapshot(state, snapshotFor(null));

  assert.equal(state.currentTask, null);
});

test("非法快照不改变状态", () => {
  const state = createAgentState();

  applyAgentSnapshot(state, null);
  applyAgentSnapshot(state, "not-an-object");

  assert.equal(state.ready, false);
  assert.equal(state.currentTask, null);
});

test("终态事件仍清空 permission（事件归约行为不变）", () => {
  const state = seedLiveTask(createAgentState());

  reduceAgentEvent(state, { type: "agent.task.cancelled", taskId: "t1" });

  assert.equal(state.currentTask.permission, null);
  assert.equal(state.currentTask.state, "cancelled");
});
