# 02: Workbench 重整

**What to build:** 核心舱/星系选择/任务舱三个子空间的按钮精简与状态化：删除与顶部 subspace tab 重复的跳转按钮，任务舱操作按钮按 Task State 九态显隐，清理仪式性调用与 scoped 样式硬编码。

**Blocked by:** 无（与 01/03 文件零交集，可并行）

**Status:** ready-for-agent

- [x] 删除"星系选择"ActionButton（:298 附近）与"返回核心舱"ActionButton（:417 附近）——顶部三 tab 已覆盖导航；核心舱 action-row 收拢为 扫描节点/加载模型(主)/切换核心/释放缓存 四钮
- [x] subspace tab（:169-181）移除对 POST `/api/model/open-galaxy` 的仪式性调用（后端仅回状态文案），保留本地切换逻辑
- [x] 任务舱按钮状态化（Task State 九态见 `doc/CONTEXT.md`，状态来源对照 `src/composables/agentState.js`）：等待计划确认→确认/拒绝计划；等待权限→允许/拒绝；运行→暂停/取消；暂停→恢复/取消；规划/取消中/已取消/已完成/失败→不显示操作钮（仅状态文案）。现有"确认/拒绝计划"与"允许/拒绝"已按条件显隐，保留其逻辑，重点收敛常驻的暂停/恢复/取消
- [x] scoped 样式硬编码清理：`.agent-state` 0.9rem→`var(--text-body-compact)`；`.agent-plan-list` 0.85rem→`var(--text-meta)`
- [x] 排布收尾：删除按钮后检查 action-row 与任务卡布局无空洞、无错位；可在本文件 scoped 样式内微调
- [x] 只改 `src/scenes/WorkbenchScene.vue`；不改 `styles/*.css`（归工单 01）、不改 AppShell 的 action 签名（删按钮只删模板引用）
- [x] 构建验证：`npm --prefix D:/LumiMate/ui/web run build -- --outDir dist-check-02 --emptyOutDir`

**Comments:**

（无）

- 2026-09-05 实现：删"星系选择/返回核心舱"两钮，核心舱 action-row 收拢为四钮；open-galaxy 两个调用点均在场景内并已删除（AppShell/useBridgeState 零改动）；任务舱按钮九态化（running→暂停+取消、paused→恢复+取消、其余态仅状态文案，判断字段 currentTask.state）；scoped 0.9rem/0.85rem 令牌化；构建通过。遗留：applyAgentSnapshot 刷新快照不回填 permission 字段、reducer 无 agent.task.cancelling 事件，建议另立 ticket。
