# 07: Runtime 真实 Agent 装配

**What to build:** 让 LumiMate Runtime 默认装配真实 AgentService：启动时按需拉起 Harness（Python SDK + node 载体），Key 从 gitignored `.env` 惰性注入，事件经 WebSocket 发布，关闭时清理 Harness 进程；`create_app(agent_enabled=True)` 提供真实闭环。

**Blocked by:** 02 (Harness Python SDK Bridge Adapter), 03 (Permission Policy), 04 (LumiMate Harness Tools), 06 (Session and Memory Persistence)

**Status:** ready-for-agent

- [ ] `services/agent/runtime.py`：build_agent_service（stores、Bridge、cordis、approval inbox/outbox、ToolProjector、Key 惰性读取）
- [ ] HarnessBridge.run_task 惰性启动；AgentService.close 清理
- [ ] `create_app(agent_enabled=True)` 装配 + WS 发布 + 关闭钩子
- [ ] 单测：load_api_key / build_agent_service / agent_enabled 路由 / bridge 自动启动
- [ ] 受控真实冒烟：start → plan → approve → complete（只读任务）

**Comments:**

- 2026-08-23 实现完成：runtime.py（Key 惰性注入、stores、cordis、approval 通道、ToolProjector）、Bridge 惰性启动 + publisher property（修复 AgentService 接线静默丢失事件的根因）、create_app(agent_enabled=True) + WS 发布 + 关闭清理。
- 真实冒烟 PASSED：start → plan → approve → complete（只读任务），§8 事件序列完整（created/planning/session.updated/tool_*/awaiting_plan_approval/running/completed）。
- 另修复：node 载体被外部清理后重建（deploy + repair + 插件重装）；桥接路径调试脚本保留于 .scratch/agent-upgrade/t7/。

