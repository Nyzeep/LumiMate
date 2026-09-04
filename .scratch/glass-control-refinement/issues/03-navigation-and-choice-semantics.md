# 03: Navigation and choice semantics

**What to build:** 用户能在侧栏导航、环境模式、人格选择和 Workbench 子空间中清楚看到当前选择，并通过键盘和辅助技术得到正确的导航或互斥选择语义。

**Blocked by:** 01 (Shared GlassControl seam).

**Status:** ready-for-agent

- [ ] Rail navigation 保留导航角色并为当前空间提供 aria-current，而不是伪装为普通选择器。
- [ ] 互斥环境、人格和 Workbench 子空间使用 ControlGroup 的 tab 或 radio 语义，任一时刻只保留一个选中项。
- [ ] 所有选中、悬停、焦点与减少动效状态共享新的玻璃呈现语言，但不改变原有 select 或 navigate 事件。
- [ ] 紧凑控制在桌面和移动收缩布局中可键盘抵达且不横向溢出。
- [ ] 前端构建和选择语义测试通过。

## Comments

Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
