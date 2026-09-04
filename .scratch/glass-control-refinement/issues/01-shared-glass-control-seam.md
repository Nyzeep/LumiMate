# 01: Shared GlassControl seam

**What to build:** 用户在任意接入空间都能获得一致、可访问、可分层的半透明控件基础；维护者只需声明控件种类、优先级和意图，而无需复制柔光、焦点、按下与减少动效逻辑。

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [x] 提供 card、icon、compact 三种控件种类，以及 primary、secondary、quiet 层级和 neutral、danger 意图。
- [x] 控件具有可访问名称、可见焦点、禁用时不触发动作、无图标时不保留空占位，并以文字与语义明确危险操作。
- [x] 建立最小前端测试基架，在共享 seam 上验证上述外部行为和减少动效约束。
- [x] 普通默认控件不持续循环动画；只允许当前 primary 或明确运行状态使用低频柔光。
- [x] 前端构建和该 slice 的测试通过，背景与环境层保持不变。

## Comments

Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
- 2026-09-04 Implemented GlassControl, a minimal Vitest/Vue Test Utils seam, six behavioral tests, and build verification.
