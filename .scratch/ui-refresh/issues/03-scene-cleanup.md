# 03: 场景死按钮清理与语义修正

**What to build:** 清理无实效/重复/语义错位的按钮与死代码；ModelDrawer 选中即关。范围限 Home/Companion/Settings/AppShell/ModelDrawer。

**Blocked by:** 无（与 01/02 文件零交集，可并行）

**Status:** ready-for-agent

- [x] `SettingsScene.vue`：删除"更新检查"轨道钮（前端无任何检查更新连线，属无实效类）；保留 切换语言/切换动效/前往关于；`AppShell.vue` 中 `toggleUpdateCheck` action 若成为孤儿则一并删除（后端设置键不动，仅前端停止写入）
- [x] `CompanionScene.vue`：四轨道钮文案与目的地对齐——"记忆片段"→"回到核心"（home）、"情绪轨迹"→"人格空间"（personality）、"对话记录"→chat（不变）、"存储概览"→storage（不变）；注意中英双语标签都要改（对照 language 切换的实现方式）
- [x] `HomeScene.vue`：删除"进入对话"ActionButton（与主 CTA"唤醒核心/开始对话"重复）；保留 陪伴空间/工作台
- [x] `AppShell.vue`：删除死 action `scanModels`、`agentListSessions`（无 UI 引用）；删除 `moveWindowBy` no-op 及其拖拽接线，`.shell-drag-region` 改用 Tauri 原生 `data-tauri-drag-region`；若原生属性与现有事件接线冲突，则仅删死代码并保留视觉区域，在报告里说明取舍
- [x] `ModelDrawer.vue`：`selectModel` 成功后关闭抽屉（对接 `closeDrawer`）
- [x] PersonalityScene 情绪钮保留不动（产品决策，见 spec）
- [x] 不改 `WorkbenchScene.vue` 与 `styles/*.css`
- [x] 构建验证：`npm --prefix D:/LumiMate/ui/web run build -- --outDir dist-check-03 --emptyOutDir`

**Comments:**

（无）

- 2026-09-05 实现：更新检查钮删除（"启动行为"卡保留为只读策略展示以维持 2x2 网格）；Companion 四钮改为 回到核心/人格空间/对话记录/存储概览（该应用无 i18n 字典，场景标签为硬编码中文，英文仅 sceneRegistry titleEn）；Home"进入对话"删除；死 action scanModels/openModelGalaxy/agentListSessions/toggleUpdateCheck/moveWindowBy 及拖拽死接线删除；拖拽取舍：不加 data-tauri-drag-region——src-tauri 无 capabilities 文件，零授权下 start_dragging 必被 ACL 拒绝，且窗口本有系统标题栏；ModelDrawer 选中即关经父级 selectDrawerModel 接线实现（组件保持纯展示）；构建通过。遗留：sceneRegistry ICON_PATHS.startup 成孤儿，后端三个端点（/api/model/scan、/api/model/open-galaxy、/api/agent/session/list）未动。
