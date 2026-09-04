import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ControlGroup from "./ControlGroup.vue";

const items = [
  { id: "quiet", label: "静谧", subtitle: "Quiet" },
  { id: "present", label: "在场", subtitle: "Present" },
  { id: "thinking", label: "思索", subtitle: "Thinking" }
];

describe("ControlGroup", () => {
  it("keeps one radio option selected and lets arrow keys move the selection", async () => {
    const wrapper = mount(ControlGroup, {
      attachTo: document.body,
      props: { ariaLabel: "情绪模式", items, selectedId: "quiet", selectionRole: "radio" }
    });

    const group = wrapper.get('[role="radiogroup"]');
    const options = group.findAll('[role="radio"]');
    expect(options).toHaveLength(3);
    expect(options[0].attributes("aria-checked")).toBe("true");
    expect(options[1].attributes("aria-checked")).toBe("false");
    expect(options[0].attributes("tabindex")).toBe("0");
    expect(options[1].attributes("tabindex")).toBe("-1");

    await options[0].trigger("keydown", { key: "ArrowRight" });
    expect(wrapper.emitted("select")).toEqual([["present"]]);
    expect(document.activeElement).toBe(options[1].element);
    wrapper.unmount();
  });

  it("expresses a Workbench subspace as tabs linked to their panels", async () => {
    const wrapper = mount(ControlGroup, {
      props: {
        ariaLabel: "工作台子空间",
        items: [
          { id: "core", label: "核心舱", panelId: "workbench-core-panel" },
          { id: "agent", label: "任务舱", panelId: "workbench-agent-panel" }
        ],
        selectedId: "agent",
        selectionRole: "tab"
      }
    });

    const tabs = wrapper.findAll('[role="tab"]');
    expect(tabs[0].attributes("aria-selected")).toBe("false");
    expect(tabs[1].attributes("aria-selected")).toBe("true");
    expect(tabs[1].attributes("aria-controls")).toBe("workbench-agent-panel");

    await tabs[0].trigger("click");
    expect(wrapper.emitted("select")).toEqual([["core"]]);
  });
});
