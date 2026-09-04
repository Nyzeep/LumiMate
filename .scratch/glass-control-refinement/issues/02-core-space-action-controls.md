# 02: Core-space action controls

**What to build:** 用户在首页、聊天、Companion 与加载空间中看到一致的主、次与静默操作层级；最重要的下一步保持靠近内容或输入，其余入口不再以多个同权大按钮争抢注意力。

**Blocked by:** 01 (Shared GlassControl seam).

**Status:** ready-for-agent

- [ ] 行动卡和轨道图标控件接入共享控制 seam，同时保留各空间现有导航、开始对话、语音和加载行为。
- [ ] 每个局部区域最多一个 primary；次操作按逻辑编组，图标控制保持紧凑且可访问。
- [ ] 首页中心入口、聊天输入附近操作与 Companion 入口在主桌面及收缩宽度下没有横向溢出。
- [ ] 既有场景色只做弱上下文强调，不再替代操作优先级或危险语义。
- [ ] 前端构建和相关共享行为测试通过。

## Comments

Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
