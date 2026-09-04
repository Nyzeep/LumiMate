# 02: Core-space action controls

**What to build:** 用户在首页、聊天、Companion 与加载空间中看到一致的主、次与静默操作层级；最重要的下一步保持靠近内容或输入，其余入口不再以多个同权大按钮争抢注意力。

**Blocked by:** 01 (Shared GlassControl seam).

**Status:** ready-for-agent

- [x] 行动卡和轨道图标控件接入共享控制 seam，同时保留各空间现有导航、开始对话、语音和加载行为。
- [x] 保留旧行动卡的 full-width block 布局与调用方 class/attribute 透传，并允许 Workbench 的无图标操作不产生空 glyph 占位。
- [x] 每个局部区域最多一个 primary；次操作按逻辑编组，图标控制保持紧凑且可访问。
- [x] 首页中心入口、聊天输入附近操作与 Companion 入口在主桌面及收缩宽度下没有横向溢出。
- [x] 既有场景色只做弱上下文强调，不再替代操作优先级或危险语义。
- [x] 前端构建和相关共享行为测试通过。

## Comments

Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
- 2026-09-04: Migrated ActionButton and OrbitalIconButton as thin GlassControl adapters. Browser geometry checks covered 1440×900, 1280×720, 980×720, and 860×720; compact desktop reflows keep Chat and Companion controls inside the clipped scene viewport, while the narrow layout retains vertical scrolling. `npm test` passed 10 tests and `npm run build` passed.
