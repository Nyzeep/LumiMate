import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ModelDrawer from "./ModelDrawer.vue";

describe("ModelDrawer", () => {
  it("presents model configurations as one selected radio choice and preserves select events", async () => {
    const wrapper = mount(ModelDrawer, {
      props: {
        open: true,
        title: "思维核心",
        name: "Lumi LLM",
        path: "C:/models/first",
        options: [
          { id: "first", title: "第一模型", subtitle: "Ready", path: "C:/models/first" },
          { id: "second", title: "第二模型", subtitle: "Local", path: "C:/models/second" }
        ]
      }
    });

    const group = wrapper.get('[role="radiogroup"]');
    const choices = group.findAll('[role="radio"]');
    expect(choices).toHaveLength(2);
    expect(choices[0].attributes("aria-checked")).toBe("true");
    expect(choices[1].attributes("aria-checked")).toBe("false");

    await choices[1].trigger("click");
    expect(wrapper.emitted("select")).toEqual([["C:/models/second"]]);
  });

  it("preserves the drawer's existing no-selection state", () => {
    const wrapper = mount(ModelDrawer, {
      props: {
        open: true,
        path: "",
        options: [{ id: "first", title: "第一模型", subtitle: "Ready", path: "C:/models/first" }]
      }
    });

    expect(wrapper.get('[role="radio"]').attributes("aria-checked")).toBe("false");
  });

  it("returns focus to the model trigger after closing", async () => {
    const trigger = document.createElement("button");
    document.body.append(trigger);
    trigger.focus();
    const wrapper = mount(ModelDrawer, { attachTo: document.body, props: { open: false } });

    await wrapper.setProps({ open: true });
    wrapper.get('button[aria-label="关闭配置"]').element.focus();
    await wrapper.setProps({ open: false });
    await wrapper.vm.$nextTick();

    expect(document.activeElement).toBe(trigger);
    wrapper.unmount();
    trigger.remove();
  });

  it("keeps a closed drawer out of the focus order", () => {
    const wrapper = mount(ModelDrawer, {
      props: { open: false }
    });

    expect(wrapper.get("aside").attributes("inert")).toBeDefined();
  });
});
