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

  it("makes a destructive action explicit to sighted and assistive-technology users", () => {
    const wrapper = mount(GlassControl, {
      props: { label: "取消任务", intent: "danger" }
    });

    expect(wrapper.text()).toContain("危险操作");
    expect(wrapper.get("button").attributes("aria-label")).toBe("危险操作：取消任务");
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

  it("honors a full-width layout request from a caller", () => {
    const wrapper = mount(GlassControl, {
      props: { label: "进入对话", kind: "card", block: true }
    });

    const control = wrapper.get("button");
    expect(control.classes()).toContain("glass-control--block");
    expect(control.attributes("data-block")).toBe("true");
  });
});
