import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import OrbitalIconButton from "./OrbitalIconButton.vue";

describe("OrbitalIconButton", () => {
  it("maps an active icon control to an accessible selected state", () => {
    const wrapper = mount(OrbitalIconButton, {
      props: { label: "情绪轨迹", iconPath: "M12 5v14", active: true }
    });

    const control = wrapper.get("button");
    expect(control.attributes("aria-label")).toBe("情绪轨迹");
    expect(control.attributes("aria-pressed")).toBe("true");
  });

  it("keeps a disabled icon operation unavailable", async () => {
    const wrapper = mount(OrbitalIconButton, {
      props: { label: "情绪轨迹", iconPath: "M12 5v14", disabled: true }
    });

    const control = wrapper.get("button");
    expect(control.attributes("disabled")).toBeDefined();
    await control.trigger("click");
    expect(wrapper.emitted("click")).toBeUndefined();
  });
});
