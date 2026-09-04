# 04: Workbench command rail

**What to build:** Workbench 用户能在任务证据和计划旁看到当前阶段唯一的主命令、编组后的辅助命令与单独标识的危险区，从而先理解任务，再安全地确认、拒绝、暂停、恢复或取消。

**Blocked by:** 01 (Shared GlassControl seam), 03 (Navigation and choice semantics).

**Status:** ready-for-agent

- [ ] 任务、计划、轨迹和证据成为主阅读列；当前阶段的一个 primary 命令进入专属命令栏。
- [ ] 计划确认、权限允许、拒绝、暂停、恢复和取消按各自状态邻近展示，不再形成五个同权动作。
- [ ] 拒绝和取消具有明确危险文字、独立区域和可达焦点，不可作为 primary-neutral 控件出现。
- [ ] 任务舱、核心舱和星系选择的现有业务状态与 action 事件保持不变。
- [ ] 命令栏在 1440×900、1280×720、980px 与 860px 下保持可读、可键盘操作且无横向溢出。
- [ ] 前端构建和 Workbench 用户可见行为测试通过。

## Comments

Layout source: prototype-ui-glass-control-language commit 67e1352, variant B.
Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
