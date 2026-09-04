import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import StorageScene from "./StorageScene.vue";

describe("StorageScene", () => {
  it("keeps cache release explicit and danger-labelled", async () => {
    const actions = { releaseCache: vi.fn() };
    const wrapper = mount(StorageScene, {
      props: {
        active: true, scene: { title: "存储", titleEn: "Storage" }, actions, state: {},
        view: { storagePercent: 20, storageUsedLabel: "2 GB", storageTotalLabel: "10 GB", storageFreeLabel: "8 GB", storageItems: [] }
      }
    });

    const release = wrapper.get('button[aria-label="危险操作：安全释放缓存"]');
    await release.trigger("click");
    expect(actions.releaseCache).toHaveBeenCalledTimes(1);
  });
});
