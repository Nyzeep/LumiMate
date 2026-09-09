import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { reactive, ref } from "vue";
import ChatScene from "./ChatScene.vue";
import { RUNTIME_CONTEXT } from "../composables/useRuntimeContext";

describe("ChatScene", () => {
  it("keeps sending form-driven with a named message input", async () => {
    const actions = { sendCurrentText: vi.fn(), setComposerText: vi.fn(), beginConversation: vi.fn(), stopVoice: vi.fn(), clearChat: vi.fn() };
    const state = reactive({
      chat: { running: false, phase: "idle", messages: [], voiceLevel: 0, status: "等待输入" },
      emotion: { presenceLevel: 0.4, breathLevel: 0.5 },
      ui: { composerText: "你好" }
    });
    const derived = {
      voicePercent: ref(20), breathPercent: ref(50), presenceCopy: ref("在线"), chatStageLabel: ref("安静"),
      presencePercent: ref(40), moodLabel: ref("平静"), progressRatio: ref(0.4), stateLabel: ref("就绪")
    };
    const wrapper = mount(ChatScene, {
      props: { active: true, scene: { title: "对话", titleEn: "Chat" } },
      global: { provide: { [RUNTIME_CONTEXT]: { state, derived, actions } } }
    });

    expect(wrapper.get('input[aria-label="消息输入"]').element.value).toBe("你好");
    expect(wrapper.get('button[aria-label="发送消息"]').attributes("type")).toBe("submit");
    await wrapper.get("form").trigger("submit");
    expect(actions.sendCurrentText).toHaveBeenCalledTimes(1);
  });
});
