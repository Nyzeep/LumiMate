# UI Refresh：字体令牌统一与按钮精简（2026-09-05）

## 背景与目标

LumiMate 前端（`ui/web`，Vue 3 + Tauri）字体与按钮存在三类病：字阶失控（约 40 处绕过 `tokens.css` 令牌的硬编码）、按钮冗余（Workbench 单场景 16 个 ActionButton，多处与 tab 重复）、语义错位（个别入口文案与目的地不符、死按钮无实效）。本 effort 以拷问定案的范围做一次收敛：**排布更合理、删除无用按钮、字体全部归入令牌体系**。

## 拷问定案（2026-09-05 会话）

- **Q1 范围**：B —— Workbench 深度重整 + 其他场景死按钮清理与语义修正 + 全站字体统一。
- **Q2 无用按钮判定**：无实效 / 入口重复 / 语义错位三类直接删；存疑类默认保留（PersonalityScene 三枚情绪钮虽不驱动后端行为，但属人格表达入口，保留，后续"情绪→氛围"接线另立 effort）。
- **Q3 功能优化**：① 合并重复入口；② 任务舱操作按钮按 Task State 九态显隐（不再常驻暂停/恢复/取消）；③ CompanionScene 导航语义修正。
- **Q4 字体策略**：仅令牌统一 + 字阶收敛到 6-7 档；不换字体栈、不引入字体文件。
- **Q5 定稿方式**：直接改真 UI 小步迭代，`npm run dev` 可脱离后端降级运行；合流后截图走查汇报。不做原型绕道。

## 事实底账（2026-09-05 Explore 盘点）

- 动作链路单一：`AppShell.vue actions → useBridgeState.js bridgeActions → runtimeClient.js runtimeCommand()`（HTTP POST `http://127.0.0.1:8765`），窗口控制走 Tauri invoke。精简按钮不伤及底层。
- 实锤无实效：设置页"更新检查"开关（无任何连线）、窗口拖拽（`moveWindowBy` no-op、Rust 无 `move_window`）、`/api/model/open-galaxy` 仪式性调用（后端仅回状态文案）、死 action `scanModels` / `agentListSessions`（无 UI 引用）。
- 实锤重复：Workbench"星系选择""返回核心舱"按钮与顶部三 tab 完全重复；Home"进入对话"与主 CTA 重复。
- 实锤语义错位：CompanionScene 四轨道钮文案与目的地不符（"记忆片段"→home 等）。
- 字体：令牌已齐（`--font-ui/--font-mono` + `--text-*` 九档），但 base/layout/components/scenes 四个 css 约 40 处硬编码（px 字号 9/10/11/13/16/18/22/30/32 九档，字重集中 200/300，行高 1.03-1.8 散布），`--line-body/--line-tight` 定义后 0 消费；唯一 .vue 硬编码在 WorkbenchScene.vue scoped 样式（0.9rem/0.85rem）。
- ModelDrawer 选中模型后不关抽屉（UX 瑕疵）。

## 工作流拆分（文件分区，工单间零共享文件，可并行）

| 工单 | 文件范围（独占） |
| --- | --- |
| 01 字体令牌统一 | `src/styles/tokens.css`、`base.css`、`layout.css`、`components.css`、`scenes.css`（`src/styles.css` 只读确认） |
| 02 Workbench 重整 | `src/scenes/WorkbenchScene.vue` |
| 03 场景死按钮清理 | `src/scenes/SettingsScene.vue`、`CompanionScene.vue`、`HomeScene.vue`、`src/app/AppShell.vue`、`src/components/ModelDrawer.vue`（必要时 `src/composables/useBridgeState.js`、`useSceneNavigation.js`） |
| 04 视觉验收 | 无文件改动（构建 + dev 截图走查 + 小修，由主会话执行） |

分区原则：`styles/*.css` 归 01 独占；Workbench 的 scoped 样式归 02；03 不碰 css 与 Workbench。

## 验收标准

- `npm run build` 通过（各工单自查 + 合流复验）。
- 死按钮清单全部处理：更新检查、进入对话（Home）、星系选择/返回核心舱（Workbench）、拖拽 no-op、死 action×2 已删；情绪钮仍在。
- 任务舱操作按钮按九态显隐；Companion 四钮文案与目的地一致；ModelDrawer 选中即关。
- `styles/*.css` 无绕过令牌的 font-size/font-weight/line-height 残留；字阶收敛后视觉近似原状。
- 9 场景 + Workbench 三子空间截图走查无排版回归。

## 非目标

- 不换字体栈、不引入 web font；不动后端（`runtime/server.py`、`controllers/` 等零改动，仅前端停止调用 open-galaxy）。
- TTS 下载卡保持占位展示；PersonalityScene 情绪钮保留。
- 不做全局视觉风格改版（配色、光效、动效均不动）。
