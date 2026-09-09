import { describe, expect, it, vi } from "vitest";
import { reactive, ref } from "vue";
import StorageScene from "./StorageScene.vue";
import { mountWithRuntimeContext } from "../test-utils/runtimeContext";

describe("StorageScene", () => {
  it("keeps cache release explicit and danger-labelled", async () => {
    const actions = { releaseCache: vi.fn() };
    const state = reactive({ runtime: { storageItems: [] } });
    const derived = {
      storagePercent: ref(20),
      storageUsedLabel: ref("2 GB"),
      storageTotalLabel: ref("10 GB"),
      storageFreeLabel: ref("8 GB")
    };
    const wrapper = mountWithRuntimeContext(
      StorageScene,
      { state, derived, actions },
      { active: true, scene: { title: "存储", titleEn: "Storage" } }
    );

    const release = wrapper.get('button[aria-label="危险操作：安全释放缓存"]');
    await release.trigger("click");
    expect(actions.releaseCache).toHaveBeenCalledTimes(1);
  });
});
