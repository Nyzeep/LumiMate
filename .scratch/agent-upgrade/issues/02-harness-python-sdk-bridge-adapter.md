# 02: Harness Python SDK Bridge Adapter

**What to build:** 让 LumiMate Runtime 能通过 Bridge 驱动 DeepSeek Harness 完成一次受控开发任务：启动/关闭 Harness Runtime、创建/恢复 Session、提交任务、订阅并映射 Agent 事件、协作式取消/暂停、失败回传，并向 UI 同步状态。Windows 上必须先完成「Python SDK + dev node 载体」Spike 验证与审批闭环验证，作为本 ticket 验收的硬前置。

**Blocked by:** 01 (Task State and Event Model)

**Status:** ready-for-agent

- [ ] Spike 闭环通过：Windows 上 `DSH_RUNTIME_MODE=node`（Node ≥ 22.19）经 Python SDK 跑通一次受控任务（文件读取 → 计划 → 确认 → 文件修改 → 允许的测试/检查），含取消、失败回传与 Bridge→UI 状态同步；失败则按 ADR 0001 回退 Node sidecar 并记录结论
- [ ] 审批闭环硬前置：先试 ACP，失败再自研 cordis 插件；结论记录到 ADR/ticket
- [ ] SDK 线协议映射测试覆盖：`session.event` / `session.status` / `subagent.started` / `subagent.finished`
- [ ] SDK 同步 API 不阻塞 FastAPI 事件循环（后台线程/执行器隔离）
- [ ] 进程终止/关闭路径：协作式取消（等待当前步骤，超时 10 秒终止 Harness 进程）；文件变更保留不回滚
- [ ] 失败语义：测试失败是结果项不是任务失败；任务失败仅指 Harness 非正常终止或显式失败；失败回传测试覆盖
- [ ] Bridge 只依赖公开 SDK API 与线协议；SDK 与 runtime-bin 精确同版本（commit `47f943859b`，rc.5），版本锁定记录
- [ ] `/api/agent/*` 路由挂载：status / task/start / task/approve / task/pause / task/resume / task/cancel / session/list / session/resume
- [ ] 现有 pytest 不回归：`python -m pytest`

**Comments:**

（无）
