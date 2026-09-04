# 04: Workbench command rail

**What to build:** Workbench 用户能在任务证据和计划旁看到当前阶段唯一的主命令、编组后的辅助命令与单独标识的危险区，从而先理解任务，再安全地确认、拒绝、暂停、恢复或取消。

**Blocked by:** 01 (Shared GlassControl seam), 03 (Navigation and choice semantics).

**Status:** ready-for-agent

- [x] 任务、计划、轨迹和证据成为主阅读列；当前阶段的一个 primary 命令进入专属命令栏。
- [x] 计划确认、权限允许、拒绝、暂停、恢复和取消按各自状态邻近展示，不再形成五个同权动作。
- [x] 拒绝和取消具有明确危险文字、独立区域和可达焦点，不可作为 primary-neutral 控件出现。
- [x] 任务舱、核心舱和星系选择的现有业务状态与 action 事件保持不变。
- [x] 命令栏在 1440×900、1280×720、980px 与 860px 下保持可读、可键盘操作且无横向溢出。
- [x] 前端构建和 Workbench 用户可见行为测试通过。

## Comments

Layout source: prototype-ui-glass-control-language commit 67e1352, variant B.
Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
- 2026-09-04: Added TaskCommandRail as the user-visible seam for phase-specific commands. It accepts the current task and status label, emits boolean plan/permission decisions plus pause/resume/cancel, and centralizes the single-current-command / explicit-danger-zone mapping. Workbench forwards those events to the unchanged agent action functions. Vitest covered plan, permission, running, reject, and cancel outcomes (16 total UI tests). Browser DOM checks with a representative reactive task confirmed task/plan → trail/evidence → command rail order, visible confirm/reject controls, and no document-level horizontal overflow at 1440×900, 1280×720, 980×720, and 860×720.
- 2026-09-04 review follow-up: Agent reducer can retain a completed permission payload when it emits running. The rail now only offers permission decisions during awaiting_permission, with a regression test proving stale permission does not displace pause/cancel. Reading order is task/plan → trail/evidence → command rail; the existing new-task form remains available as a secondary action while a current task owns the rail primary. Snapshot-restored awaiting_permission has no permission contract payload, so the rail explicitly says details are recovering and offers only the already-supported danger cancel action rather than inventing allow/reject identifiers; a Workbench-level test covers that action forwarding.
- 2026-09-04 correction: The earlier browser-check history described the pre-review order. The final rail placement is task/plan → trail/evidence → command rail, so users read all available task facts before the phase decision.
- 2026-09-04 history clarification: The first comment entry is restored verbatim as the prior tracker record; the correction records the transient review draft. The implemented and accepted reading order remains task/plan → trail/evidence → command rail.
