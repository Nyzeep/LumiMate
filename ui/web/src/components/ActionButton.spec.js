import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ActionButton from "./ActionButton.vue";

describe("ActionButton", () => {
  it("preserves a hero caller's accessible action, custom attribute, and click behavior", async () => {
    const wrapper = mount(ActionButton, {
      props: {
        label: "进入对话",
        subtitle: "Chat Space",
        iconPath: "M12 5v14",
        tier: "primary",
        block: true
      },
      attrs: { class: "hero-cta", "data-source": "home" }
    });

    const control = wrapper.get("button");
    expect(control.attributes("aria-label")).toBe("进入对话");
    expect(control.attributes("data-source")).toBe("home");

    await control.trigger("click");
    expect(wrapper.emitted("click")).toHaveLength(1);
  });

  it("renders a Workbench command without a phantom glyph", () => {
    const wrapper = mount(ActionButton, {
      props: { label: "确认计划", subtitle: "Approve", tier: "primary" }
    });

    expect(wrapper.find("svg").exists()).toBe(false);
  });
});
