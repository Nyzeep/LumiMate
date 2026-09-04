# 06: Cross-space motion and visual acceptance

**What to build:** 用户获得完整、安静且一致的控制体验；所有已迁移空间在不同窗口尺寸和减少动效模式下都保持清晰，且原有背景与整体色调没有回归。

**Blocked by:** 02 (Core-space action controls), 03 (Navigation and choice semantics), 04 (Workbench command rail), 05 (Supporting native control migration).

**Status:** ready-for-agent

- [ ] 对已迁移空间审查每个局部区域的 primary 数量、危险意图、文字标签、焦点与禁用行为。
- [ ] 确认普通控件默认不持续动画，减少动效模式移除新增无限动画，当前运行或 primary 的柔光保持克制。
- [ ] 在 1440×900、1280×720、980px 和 860px 进行浏览器视觉验收，并在 Tauri WebView2 spot-check 半透明、泛光和布局。
- [ ] 确认背景资产、环境层和深蓝琥珀色域未被控件改造替换或覆盖。
- [ ] 完整前端构建、前端测试和现有 Runtime 烟雾检查通过。

## Comments

Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
