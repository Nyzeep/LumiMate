# 01: Task State and Event Model

**What to build:** 让 LumiMate Runtime 在完全不依赖真实 Harness 连接的情况下，能创建受控开发任务、按提案 §9 的十个状态推进生命周期、拒绝一切非法状态转换，并按提案 §8 发出结构稳定的 `agent.*` 事件。任务、Session 与 Grant 具备内存与落盘模型，Runtime 重启后非终态任务统一进入 `paused` 并标记 `interrupted: true`。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 状态转换表与提案 §9 一致：十个状态（`draft / planning / awaiting_plan_approval / awaiting_permission / running / paused / cancelling / cancelled / completed / failed`）全覆盖
- [ ] 允许的转换全部可执行并产生正确事件；禁止的转换全部被拒绝，包括：终态回非终态、`cancelling` 回 `running`/`paused`、跳过 `awaiting_plan_approval` 从 `draft` 直入 `running`、从 `planning`/`running` 直入 `completed`、权限待确认时自动进入 `running`
- [ ] 重启恢复：非终态任务落盘后重启进入 `paused + interrupted: true`；恢复边界为最近一次 turn（idle）边界
- [ ] 事件 payload 结构稳定：§8 的 `agent.*` 事件统一带 `taskId`，涉及 Session 的带 `sessionId`；字段与提案 §8 一致
- [ ] Task/Session/Grant 模型可用：Grant 可表达 `taskId + sessionId + workspace + category` 四元组
- [ ] 纯 Python 测试通过：`python -m pytest`（现有测试不回归）

**Comments:**

- 2026-08-23 code-review 澄清：Session/Grant 的落盘与恢复索引（含 idle 边界）属 T6 显式范围；T1 只提供 Task 落盘 + Task/Session/Grant 内存模型。
- running -> cancelling 在 §8 无对应事件类型，转换→事件映射显式返回 None（由状态快照表达取消中）；其余 §9 允许转换均映射到 §8 事件。
- running -> completed 的“明确成功判定”由调用方（T2 Bridge）在 RunResult.completed 时触发；状态机只校验允许边。

