# 01: 字体令牌统一

**What to build:** 把 `src/styles/` 四个 css 中约 40 处绕过令牌的 font-size / font-weight / line-height 硬编码归入 `tokens.css` 令牌体系，收敛字阶、保持视觉近似。不换字体栈、不引入字体文件。

**Blocked by:** 无（与 02/03 文件零交集，可并行）

**Status:** ready-for-agent

- [x] `tokens.css`：新增 `--text-micro: 10px`、`--text-title: 16px`；新增字重 `--weight-display: 200`、`--weight-light: 300`；行高令牌接线：新增 `--line-display: 1.05`、`--line-heading: 1.6`，激活现有 `--line-body: 1.72`（`--line-tight` 保留备用）；`--font-ui`/`--font-mono` 不动
- [x] 硬编码映射（最近字阶）：9/10px→micro；11px→status；13px→meta；16px→title；18px→card；22px→card；30/32px→section。字重：200→weight-display、300→weight-light。行高：1.03→line-display；1.6/1.65→line-heading；1.7/1.78/1.8→line-body
- [x] 只动字体类声明（font-size/font-weight/line-height），不动布局属性（margin/padding/grid/width/color）
- [x] 禁止改动任何 `.vue` 文件（WorkbenchScene.vue 的 scoped 硬编码归工单 02）；发现其他 `.vue` 内硬编码只记录在报告里
- [x] `src/styles.css` 只读确认其为聚合入口即可，若确有字体硬编码则属本工单范围
- [x] 构建验证：`npm --prefix D:/LumiMate/ui/web run build -- --outDir dist-check-01 --emptyOutDir`（独立 outDir，避免与其他工单撞 dist）

**Comments:**

（无）

- 2026-09-05 实现：42 处硬编码归入令牌（新增 --text-micro/--text-title、--weight-display/--weight-light、--line-display/--line-heading，激活 --line-body 六处消费）；styles/*.css 零布局属性改动；构建一次通过。合法令牌表达式保留：components.css:755 calc、scenes.css:442 clamp。全仓 .vue 硬编码仅 WorkbenchScene 两处（归 02 处理）。
