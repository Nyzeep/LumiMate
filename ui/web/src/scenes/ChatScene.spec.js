import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import ChatScene from "./ChatScene.vue";

describe("ChatScene", () => {
  it("keeps sending form-driven with a named message input", async () => {
    const actions = { sendCurrentText: vi.fn(), setComposerText: vi.fn(), beginConversation: vi.fn(), stopVoice: vi.fn(), clearChat: vi.fn() };
    const wrapper = mount(ChatScene, {
      props: {
        active: true, scene: { title: "对话", titleEn: "Chat" }, actions,
        state: { chat: { running: false, phase: "idle", messages: [], voiceLevel: 0, status: "等待输入" }, emotion: { presenceLevel: 0.4, breathLevel: 0.5 }, ui: { composerText: "你好" } },
        view: { voicePercent: 20, breathPercent: 50, presenceCopy: "在线", chatStageLabel: "安静", presencePercent: 40, moodLabel: "平静", progressRatio: 0.4, stateLabel: "就绪" }
      }
    });

    expect(wrapper.get('input[aria-label="消息输入"]').element.value).toBe("你好");
    expect(wrapper.get('button[aria-label="发送消息"]').attributes("type")).toBe("submit");
    await wrapper.get("form").trigger("submit");
    expect(actions.sendCurrentText).toHaveBeenCalledTimes(1);
  });
});
