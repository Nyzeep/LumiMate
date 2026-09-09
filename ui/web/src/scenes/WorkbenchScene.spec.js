import { describe, expect, it, vi } from "vitest";
import { reactive, ref } from "vue";
import WorkbenchScene from "./WorkbenchScene.vue";
import { applyAgentSnapshot, createAgentState } from "../composables/agentState";
import { mountWithRuntimeContext } from "../test-utils/runtimeContext";

function createContext() {
  const currentTask = {
    taskId: "task-1", title: "当前任务", state: "running", plan: [], permission: null, failure: null, tools: [], fileChanges: [], testResults: []
  };
  const actions = {
    agentStartTask: vi.fn(),
    openModelGalaxy: vi.fn(),
    selectModel: vi.fn(), openDrawer: vi.fn(), scanComponents: vi.fn(), loadModels: vi.fn(), switchModels: vi.fn(), releaseCache: vi.fn(),
    startModelDownload: vi.fn(), cancelModelDownload: vi.fn(), agentApprovePlan: vi.fn(), agentApprovePermission: vi.fn(), agentPauseTask: vi.fn(), agentResumeTask: vi.fn(), agentCancelTask: vi.fn(), agentResumeSession: vi.fn()
  };
  const state = reactive({
    runtime: {
      state: "idle",
      loaded: false,
      message: "稳定",
      componentStatus: {
        missingRequired: [],
        asr: { kind: "asr", label: "ASR", ready: true, count: 1, status: "ready", note: "" },
        llm: { kind: "llm", label: "LLM", ready: true, count: 1, status: "ready", note: "" },
        tts: { kind: "tts", label: "TTS", ready: true, count: 1, status: "ready", note: "" }
      },
      downloadState: "idle",
      downloadProgress: 0,
      downloadMessage: "",
      downloadLogs: [],
      downloadCatalog: { asr: [], llm: [] },
      modelCatalog: { llm: [], asr: [], tts: [] }
    },
    agent: { currentTask, sessions: [] }
  });
  const derived = {
    progressRatio: ref(0), stateLabel: ref("就绪"), runtimeMessage: ref("稳定"), shortLogs: ref([]),
    currentModelName: ref("模型"), currentAsrName: ref("ASR"), currentTtsName: ref("TTS")
  };
  return {
    scene: { title: "工作台", titleEn: "Workbench" },
    active: true,
    state,
    derived,
    actions
  };
}

function mountScene(context) {
  return mountWithRuntimeContext(WorkbenchScene, context, {
    scene: context.scene,
    active: context.active
  });
}

describe("WorkbenchScene", () => {
  it("keeps starting another task available while a current task owns the command rail", async () => {
    const context = createContext();
    const wrapper = mountScene(context);

    const subspaces = wrapper.get('[aria-label="工作台子空间"]').findAll('[role="radio"]');
    await subspaces[2].trigger("click");

    await wrapper.get('input[placeholder="任务标题"]').setValue("后续任务");
    await wrapper.get('textarea[placeholder^="任务目标"]').setValue("继续整理命令栏");
    await wrapper.get('button[aria-label="发起任务"]').trigger("click");
    expect(context.actions.agentStartTask).toHaveBeenCalledWith("后续任务", "继续整理命令栏");
  });

  it("keeps rich model inspection actions available through shared controls", async () => {
    const context = createContext();
    context.state.runtime.modelCatalog.llm = [{ id: "llm-1", path: "C:/models/llm-1", title: "推理核心", subtitle: "Ready", status: "ready", selected: true, tags: ["local"] }];
    const wrapper = mountScene(context);

    await wrapper.get('button[aria-label="检查模型：推理核心"]').trigger("click");
    expect(context.actions.selectModel).toHaveBeenCalledWith("llm", "C:/models/llm-1");
    expect(context.actions.openDrawer).toHaveBeenCalledWith("llm");
  });

  it("keeps provider choice and download forwarding accessible", async () => {
    const context = createContext();
    context.state.runtime.downloadCatalog.asr = [{
      id: "asr-entry", title: "听觉模型", subtitle: "Small", sizeLabel: "1 GB", providers: { modelscope: "ms/asr", huggingface: "hf/asr" }
    }];
    const wrapper = mountScene(context);
    const subspaces = wrapper.get('[aria-label="工作台子空间"]').findAll('[role="radio"]');
    await subspaces[1].trigger("click");

    const provider = wrapper.get('[aria-label="ASR 下载来源"]');
    await provider.get('button[aria-label="HF"]').trigger("click");
    await wrapper.get('button[aria-label="下载模型：听觉模型"]').trigger("click");
    expect(context.actions.startModelDownload).toHaveBeenCalledWith("asr", "huggingface", "hf/asr", "听觉模型");
  });

  it("keeps a snapshot-restored permission wait safely cancellable", async () => {
    const context = createContext();
    const agent = createAgentState();
    applyAgentSnapshot(agent, {
      ready: true,
      harnessAvailable: true,
      currentTask: { taskId: "task-reconnect", title: "恢复中的权限", state: "awaiting_permission", plan: [] },
      sessions: []
    });
    context.state.agent = agent;

    const wrapper = mountScene(context);
    const subspaces = wrapper.get('[aria-label="工作台子空间"]').findAll('[role="radio"]');
    await subspaces[2].trigger("click");

    const rail = wrapper.get('[aria-label="任务命令"]');
    expect(rail.text()).toContain("权限请求详情正在恢复");
    await rail.get('button[aria-label="危险操作：取消任务"]').trigger("click");
    expect(context.actions.agentCancelTask).toHaveBeenCalledWith("task-reconnect");
  });
});
