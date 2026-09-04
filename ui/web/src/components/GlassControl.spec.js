import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import GlassControl from "./GlassControl.vue";

describe("GlassControl", () => {
  it("lets a user invoke an enabled labelled primary action", async () => {
    const wrapper = mount(GlassControl, {
      props: { label: "确认计划", priority: "primary" }
    });

    const control = wrapper.get("button");
    expect(control.text()).toContain("确认计划");
    expect(control.attributes("aria-label")).toBe("确认计划");

    await control.trigger("click");
    expect(wrapper.emitted("click")).toHaveLength(1);
  });

  it("keeps a disabled operation unavailable and does not emit a click", async () => {
    const wrapper = mount(GlassControl, {
      props: { label: "确认计划", disabled: true }
    });

    const control = wrapper.get("button");
    expect(control.attributes("disabled")).toBeDefined();
    expect(control.attributes("aria-disabled")).toBe("true");

    await control.trigger("click");
    expect(wrapper.emitted("click")).toBeUndefined();
  });

  it("keeps danger wording in the accessible name when a caller supplies custom copy", () => {
    const wrapper = mount(GlassControl, {
      props: { label: "取消任务", intent: "danger", ariaLabel: "终止当前执行" }
    });

    expect(wrapper.text()).toContain("危险操作");
    expect(wrapper.get("button").attributes("aria-label")).toBe("危险操作：终止当前执行");
  });

  it("does not reserve a glyph when the caller supplies no icon", () => {
    const wrapper = mount(GlassControl, {
      props: { label: "继续", kind: "compact" }
    });

    expect(wrapper.find("svg").exists()).toBe(false);
  });

  it("exposes selected state when a caller asks for a toggle", () => {
    const wrapper = mount(GlassControl, {
      props: { label: "任务舱", selected: true }
    });

    expect(wrapper.get("button").attributes("aria-pressed")).toBe("true");
  });

  it("supports submit controls with caller-owned rich content", () => {
    const wrapper = mount(GlassControl, {
      props: { label: "发送消息", buttonType: "submit", kind: "icon" },
      slots: { default: '<span class="send-copy">发送</span>' }
    });

    expect(wrapper.get("button").attributes("type")).toBe("submit");
    expect(wrapper.get(".send-copy").text()).toBe("发送");
  });

  it("remains reachable through the keyboard focus order", () => {
    const wrapper = mount(GlassControl, {
      attachTo: document.body,
      props: { label: "确认计划" }
    });

    const control = wrapper.get("button").element;
    control.focus();
    expect(document.activeElement).toBe(control);
    wrapper.unmount();
  });
});
