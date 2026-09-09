import { mount } from "@vue/test-utils";
import { RUNTIME_CONTEXT } from "../composables/useRuntimeContext";

export function mountWithRuntimeContext(component, context, props = {}) {
  return mount(component, {
    props,
    global: {
      provide: { [RUNTIME_CONTEXT]: context }
    }
  });
}
