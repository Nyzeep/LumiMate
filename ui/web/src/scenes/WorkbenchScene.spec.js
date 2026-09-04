import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import WorkbenchScene from "./WorkbenchScene.vue";
import { applyAgentSnapshot, createAgentState } from "../composables/agentState";

function createProps() {
  const currentTask = {
    taskId: "task-1", title: "当前任务", state: "running", plan: [], permission: null, failure: null, tools: [], fileChanges: [], testResults: []
  };
  const actions = {
    agentStartTask: vi.fn(),
    openModelGalaxy: vi.fn(),
    selectModel: vi.fn(), openDrawer: vi.fn(), scanComponents: vi.fn(), loadModels: vi.fn(), switchModels: vi.fn(), releaseCache: vi.fn(),
    startModelDownload: vi.fn(), cancelModelDownload: vi.fn(), agentApprovePlan: vi.fn(), agentApprovePermission: vi.fn(), agentPauseTask: vi.fn(), agentResumeTask: vi.fn(), agentCancelTask: vi.fn(), agentResumeSession: vi.fn()
  };
  return {
    scene: { title: "工作台", titleEn: "Workbench" }, active: true, actions,
    state: {
      runtime: { state: "idle", componentStatus: { missingRequired: [], asr: { kind: "asr", label: "ASR", ready: true, count: 1, status: "ready", note: "" }, llm: { kind: "llm", label: "LLM", ready: true, count: 1, status: "ready", note: "" }, tts: { kind: "tts", label: "TTS", ready: true, count: 1, status: "ready", note: "" } }, downloadState: "idle", downloadProgress: 0, downloadMessage: "", downloadCatalog: { asr: [], llm: [] } },
      agent: { currentTask, sessions: [] }
    },
    view: {
      progressRatio: 0, stateLabel: "就绪", runtimeMessage: "稳定", shortLogs: [], currentModelName: "模型", currentAsrName: "ASR", currentTtsName: "TTS",
      modelCatalog: { llm: [], asr: [], tts: [] }, agent: { currentTask, sessions: [] }
    }
  };
}

describe("WorkbenchScene", () => {
  it("keeps starting another task available while a current task owns the command rail", async () => {
    const props = createProps();
    const wrapper = mount(WorkbenchScene, { props });

    const subspaces = wrapper.get('[aria-label="工作台子空间"]').findAll('[role="radio"]');
    await subspaces[2].trigger("click");

    await wrapper.get('input[placeholder="任务标题"]').setValue("后续任务");
    await wrapper.get('textarea[placeholder^="任务目标"]').setValue("继续整理命令栏");
    await wrapper.get('button[aria-label="发起任务"]').trigger("click");
    expect(props.actions.agentStartTask).toHaveBeenCalledWith("后续任务", "继续整理命令栏");
  });

  it("keeps a snapshot-restored permission wait safely cancellable", async () => {
    const props = createProps();
    const agent = createAgentState();
    applyAgentSnapshot(agent, {
      ready: true,
      harnessAvailable: true,
      currentTask: { taskId: "task-reconnect", title: "恢复中的权限", state: "awaiting_permission", plan: [] },
      sessions: []
    });
    props.state.agent = agent;
    props.view.agent = agent;

    const wrapper = mount(WorkbenchScene, { props });
    const subspaces = wrapper.get('[aria-label="工作台子空间"]').findAll('[role="radio"]');
    await subspaces[2].trigger("click");

    const rail = wrapper.get('[aria-label="任务命令"]');
    expect(rail.text()).toContain("权限请求详情正在恢复");
    await rail.get('button[aria-label="危险操作：取消任务"]').trigger("click");
    expect(props.actions.agentCancelTask).toHaveBeenCalledWith("task-reconnect");
  });
});
