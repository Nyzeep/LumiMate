import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import RailNav from "./RailNav.vue";

describe("RailNav", () => {
  it("marks the current space as navigation instead of a radio choice", async () => {
    const wrapper = mount(RailNav, {
      props: {
        groups: [{ id: "primary", title: "主空间" }],
        scenes: [
          { id: "home", title: "首页", titleEn: "Home" },
          { id: "chat", title: "对话空间", titleEn: "Chat" }
        ],
        currentScene: "chat",
        currentGroup: 0
      }
    });

    const nav = wrapper.get('nav[aria-label="空间导航"]');
    const sceneButtons = nav.findAll('.rail-nav__button');
    expect(sceneButtons[0].attributes("aria-current")).toBeUndefined();
    expect(sceneButtons[1].attributes("aria-current")).toBe("page");
    expect(nav.find('[role="radiogroup"]').exists()).toBe(false);

    await sceneButtons[0].trigger("click");
    expect(wrapper.emitted("navigate")).toEqual([["home"]]);
  });
});
