# 03: Permission Policy

**What to build:** 让 Task Agent 的工具调用按风险分级受控：Low 自动执行、Medium 在当前 Task 内按操作类别授权后连续执行、High 每次操作都需用户确认；Medium Grant 绑定 `taskId + sessionId + workspace + category`，任务终态后自动失效；不存在任何自动提升路径。

**Blocked by:** 01 (Task State and Event Model), 02 (Harness Python SDK Bridge Adapter)

**Status:** ready-for-agent

- [ ] 风险分级与提案 §13 一致：Low（读取/搜索/分析目录/Git 状态/生成计划/查看测试结果）、Medium（`file_modify` / `test` / `lint` / `typecheck`）、High（删除文件、修改依赖、关键配置、安装命令、网络、Workspace 外路径、启动系统程序、修改系统设置）
- [ ] Medium 按类别授权：第一类首次确认后同 Task 内同类连续执行；跨类别需再次确认；不逐命令确认；不跨 Task 复用
- [ ] Grant 四元组校验：`taskId + sessionId + workspace + category`；Task 结束、取消、失败或 Workspace 改变后自动失效
- [ ] High 每次操作都需确认；拒绝越权工具调用（无 Grant 或超出授权类别）
- [ ] 无自动提升路径测试覆盖：情绪、陪伴关系、使用时长、历史成功率、信任程度、Agent 自身判断均不得提升权限
- [ ] 权限待确认时不得自动进入 `running`
- [ ] 安全测试覆盖并通过：`python -m pytest`

**Comments:**

（无）
- 2026-08-23 实现：RiskLevel/classify_action（§13 全表）、PermissionPolicy（四元组 Grant、终态/Workspace 失效、无自动提升）、AgentService 工具拦截（无 Grant → awaiting_permission + §8 事件）、approve_permission（Medium 建 Grant、High 单次放行）、HarnessBridge.answer_approval（写插件 inbox）、路由 kind=permission。
