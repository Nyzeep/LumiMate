# 05: Supporting native control migration

**What to build:** 用户在设置、模型抽屉、会话行、聊天坞和窗口级控制中获得与核心空间一致的玻璃层级与状态反馈，同时不失去这些控件各自的业务语义。

**Blocked by:** 01 (Shared GlassControl seam), 02 (Core-space action controls).

**Status:** ready-for-agent

- [ ] 原生复杂控件接入共享状态与呈现约定，但保留其现有内容结构和业务事件。
- [ ] 抽屉、模型选项、会话行、发送与设置操作分别拥有明确的主、次、静默或危险层级。
- [ ] 窗口关闭保持独立危险态，最小化和最大化保持系统级紧凑控制；业务行为不改变。
- [ ] 不为场景特例新增浅层按钮包装，公共行为仍集中在共享 seam。
- [ ] 前端构建和相关可访问行为测试通过。

## Comments

Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
