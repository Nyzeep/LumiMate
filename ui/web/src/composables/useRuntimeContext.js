// 运行时上下文接缝：组合根（AppShell）单点实例化并 provide，
// Scene 通过 useRuntimeContext 消费 { state, derived, actions }。
// props 只承载真正"每个实例不同"的数据（scene 元信息、active 标志）。
import { inject, provide } from "vue";

export const RUNTIME_CONTEXT = Symbol("RUNTIME_CONTEXT");

export function provideRuntimeContext(context) {
  provide(RUNTIME_CONTEXT, context);
}

export function useRuntimeContext() {
  const context = inject(RUNTIME_CONTEXT);
  if (!context) {
    throw new Error("useRuntimeContext 必须在 provideRuntimeContext 之后的组件树内使用");
  }
  return context;
}
