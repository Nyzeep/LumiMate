# 01：运行时上下文 inject 接缝（9 Scene + AppShell）

**Blocks:** 无（首单）
**Blocked-by:** 无

按 spec.md 定案实施：

1. 新建 `src/composables/useRuntimeContext.js`：`RUNTIME_CONTEXT` Symbol + `provideRuntimeContext()` + `useRuntimeContext()`（缺失时抛错）。
2. `useBridgeState`：`derived.loadingSteps`（含 AppShell 的 FALLBACK_LOADING_STEPS 兜底）；删除 `syncAll`（零引用）。
3. `AppShell`：删 `view` computed 与 FALLBACK 常量；provide 上下文；模板 scene 只传 `:scene`/`:active`；自身 `view.bootPhaseCopy` → 解构 derived；`beginConversation` 内 `view.value.conversationReady` → `derived.conversationReady.value`。
4. 9 个 Scene：props 缩为 `{scene, active}`；`useRuntimeContext()` 取 `state/derived/actions`；`props.view.x` 按归属改写（state 直读或 derived 解构，script 内加 `.value`）。
5. 3 个 Scene spec（Workbench/Chat/Storage）：改为 provide mock 上下文（新建测试助手）。
6. 验证：vitest、test:agent、build、pytest。
