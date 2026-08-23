# 06: Session and Memory Persistence

**What to build:** 让任务与记忆在 Runtime 重启后仍可恢复：Session 只保存投影（ID、状态、标题、摘要、最近结果、恢复索引），不复制完整 Harness 事件日志；Memory 必须经过「Agent 提议 → 用户确认 → LumiMate 保存」三步才落盘，未经确认不保存。

**Blocked by:** 01 (Task State and Event Model), 02 (Harness Python SDK Bridge Adapter)

**Status:** ready-for-agent

- [ ] Session 投影落盘与恢复索引；重启后非终态任务恢复为 `paused + interrupted: true`，可用同 `sessionId` 续跑
- [ ] 投影只保存 ID、状态、标题、摘要、最近结果、恢复索引；不复制全量事件日志
- [ ] Memory 三步流程：Agent 提议 → 用户确认 → LumiMate 保存；未经确认不保存（含拒绝路径测试）
- [ ] `/api/agent/session/list`、`/api/agent/session/resume`、`/api/agent/memory/propose`、`/api/agent/memory/confirm` 路由可用
- [ ] 基础事件（`agent.session.updated` / `agent.memory.proposed`）已按 §8 发出；完整功能依赖 T2（显式声明）
- [ ] 测试通过：`python -m pytest`

**Comments:**

（无）
- 2026-08-23 实现：ProjectionStore（投影字段白名单落盘，不含事件日志）、MemoryStore（三步流程：propose pending → confirm 接受才写入，拒绝丢弃，未知/重复报错）、AgentService 重启恢复（任务 paused+interrupted + 投影恢复）、memory propose/confirm 路由与事件；全套验证通过。
