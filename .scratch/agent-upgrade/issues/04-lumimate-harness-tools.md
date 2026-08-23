# 04: LumiMate Harness Tools

**What to build:** 让 Task Agent 通过受限工具集完成受控开发：文件读取/修改、Git 状态读取、白名单测试命令（`python -m pytest`、`npm run build`、`python runtime/server.py --check`）；所有工具调用受 Permission Policy 约束，工具边界产生 `tool_started` / `tool_finished` / `test_result` 事件，文件变更产生可追踪的 `file_changed` 事件。

**Blocked by:** 02 (Harness Python SDK Bridge Adapter), 03 (Permission Policy)

**Status:** ready-for-agent

- [ ] 工具白名单校验：非白名单工具/命令被拒绝
- [ ] 工具调用前权限拦截：Low 自动、Medium 需 Grant、High 每次确认
- [ ] 工具结果规范化 → `agent.task.tool_started` / `agent.task.tool_finished` / `agent.task.test_result` 事件
- [ ] 文件变更可追踪：`agent.task.file_changed` 含 `path` / `operation` / `beforeHash` / `afterHash`
- [ ] Spike 中使用工具修改文件并执行 pytest；文件变更可追踪
- [ ] 测试命令白名单与提案 §13、§20 一致（pytest / npm run build / `python runtime/server.py --check`）
- [ ] 测试通过：`python -m pytest`

**Comments:**

（无）
