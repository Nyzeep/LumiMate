# Frontend Runtime Seam（C10 前端传话链收拢）

**Status:** ready-for-agent

来源：improve-codebase-architecture 审查候选 C10（报告 2026-09-06）。grilling 定案记录于同一会话（Q1-Q4 + 两轮补充确认）。

## 问题

每个 Agent/运行时命令要穿 4 层才能落到界面：`runtimeCommand` → `useBridgeState.bridgeActions` → `AppShell.actions`（17 个纯转发）→ Scene props。AppShell 的 `view` computed 机械解包 ~35 个字段（0 行新信息，除 loadingSteps 兜底）。三层过不了删除测试：删掉行为不变。

## 定案（grilling 共识）

1. **通道：provide/inject**。AppShell 保持单点实例化 `useBridgeState()`，provide 一份运行时上下文；Scene 用 `useRuntimeContext()` inject。Scene props 只留 `scene`/`active`。不引 Pinia、不用模块级单例（可变全局状态伤测试隔离）。
2. **命令面：单一 `actions`**。Scene 只见 `state`、`derived`、`actions` 三样。`actions` 由组合根装配：纯运行时命令直接引用 `bridgeActions` 成员、组合命令（`beginConversation` 等）留在组合根（依赖 navigate/noteActivity）、UI 状态操作（抽屉、语言）。`bridgeActions` 从 Scene 世界退到内部接缝（仍由 useBridgeState 导出）。
3. **解散 `view`**：loadingSteps 兜底逻辑移进 `derived.loadingSteps`（本来就是派生值）；直接读 state 的字段让 Scene 直接读 state；derived 标签 Scene 在 script setup 顶层解构（解构后的 ref 在模板中自动解包；script 内用 `.value`）。
4. **范围**：9 个 Scene + AppShell + useBridgeState + 3 个 Scene spec 一次迁完，不留两套机制并存的中间态。WorkbenchScene 内部 Subspace 模板重复不在本次范围。
5. **行为约束：零行为变化**。文案、时序、样式类名全部保持；确认零引用的死代码允许顺手删（`syncAll`）；疑似 bug 只记工单不顺手修。

## 接口契约

```
RUNTIME_CONTEXT（Symbol，useRuntimeContext.js 导出）
provideRuntimeContext({ state, derived, actions })   ← 仅 AppShell 调用
useRuntimeContext() → { state, derived, actions }    ← Scene 调用；缺失时抛错
```

## 验收

- Scene 不再声明 `state/view/actions` props；AppShell 模板不再下发它们。
- AppShell 无 `view` computed；无对 `bridgeActions` 成员的"仅转发再转发"链。
- `derived.loadingSteps` 存在且含原兜底逻辑；`syncAll` 删除。
- vitest 全绿（34+）、test:agent 全绿（6）、build 通过、pytest 不受影响（314）。
