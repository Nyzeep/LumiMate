# 05: Workbench Agent UI

**What to build:** 让用户能在 Workbench 空间完整看到并操作受控开发任务：三态首屏（空态引导、进行中任务、历史 Session），任务面板展示 Plan / Todo / 当前步骤 / 工具调用 / 文件变更 / 测试结果 / 权限请求 / 失败原因，并提供暂停、恢复、取消与审批操作；前端按 `event.type` 分发 `agent.*` 事件。

**Blocked by:** 02 (Harness Python SDK Bridge Adapter), 04 (LumiMate Harness Tools)

**Status:** ready-for-agent

- [ ] 三态首屏渲染：无任务空态引导 + 最近 Session 入口；有进行中任务时聚焦该任务；只有历史 Session 时显示 Session 列表
- [ ] `useBridgeState.js` 按 `event.type` 分发 `agent.*` 事件（不能只依赖 `state` 字段）
- [ ] 任务面板展示完整轨迹：Plan、Todo、当前步骤、工具调用、文件变更、测试结果、权限请求、失败原因
- [ ] 操作按钮与 API 联动：approve / pause / resume / cancel 正确调用 `/api/agent/*`
- [ ] 不把 Agent 过程塞入 Chat；保留 Workbench 现有 core/galaxy 子空间
- [ ] 构建通过：`npm run build`；现有 UI 不回归
- [ ] 后端冒烟：`python runtime/server.py --check`

**Comments:**

（无）
- 2026-08-23 实现：composables/agentState.js 纯 reducer（三态归约、§8 事件更新，Node 验证 PASSED）；useBridgeState 按 event.type 分发 agent.* + /api/agent/status 初始加载 + bridgeActions.agent*；WorkbenchScene 新增「任务舱」子空间（保留 core/galaxy：三态首屏、任务面板、权限/计划确认、暂停/恢复/取消、Session 列表）；AppShell 动作接线；npm run build 通过。
