import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { reactive, ref } from "vue";
import StorageScene from "./StorageScene.vue";
import { RUNTIME_CONTEXT } from "../composables/useRuntimeContext";

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
    const wrapper = mount(StorageScene, {
      props: { active: true, scene: { title: "存储", titleEn: "Storage" } },
      global: { provide: { [RUNTIME_CONTEXT]: { state, derived, actions } } }
    });

    const release = wrapper.get('button[aria-label="危险操作：安全释放缓存"]');
    await release.trigger("click");
    expect(actions.releaseCache).toHaveBeenCalledTimes(1);
  });
});
