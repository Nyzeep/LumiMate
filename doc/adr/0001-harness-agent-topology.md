# 0001：Harness 作为 Task Agent 执行基础设施（Python SDK 拓扑）

Status: accepted（2026-08-23；Windows 路径决策已经用户确认）

LumiMate 需要可控、可审计、可恢复的 Agent 任务能力，DeepSeek Harness 提供 Agent loop、会话持久化、工具、审批等能力。决定第一阶段由 LumiMate Python FastAPI Runtime 通过 Harness Python SDK 以子进程 + newline-delimited JSON-RPC 驱动 Harness Agent，前端只连接 LumiMate HTTP/WebSocket，不直连 Harness，也不把 Harness TypeScript 源码嵌入 Tauri。

## Considered Options

- Vue/Tauri UI 直接连接 Harness：拒绝。会破坏运行时单一入口、权限边界与事件投影。
- 把 Harness TypeScript 源码嵌入 Tauri：拒绝。增加 Node 版本与前端构建耦合，且隔离不了 developer preview 的兼容性变化。
- Node sidecar（不经 Python SDK）：保留为回退方案。仅当“Windows 上经 Python SDK 启动 Harness Runtime”验证不可用时启用。

## 已核实的平台事实（2026-08-23）

- Harness 仓库版本 `0.1.0-rc.5`（`package.json`）。
- Python SDK（`deepseek-harness-sdk`）与运行时载体包（`deepseek-harness-runtime-bin`）在本地 checkout 中均为 dev 版本（`0.0.0.dev0` / `0.0.0-dev`），仓库版本 `0.1.0-rc.5`（commit `47f943859b`）。
- `deepseek-harness-runtime-bin` 的 `platforms.json` 仅包含 linux-x64、linux-arm64、macos-arm64；**没有 Windows 官方 wheel/单文件可执行载体**。
- SDK runtime 还提供 dev-only 的 `node` 载体（Node >= 22.19，本机为 v24.14.1）：以 `DSH_RUNTIME_MODE=node` 显式选择，通过 `node .../packaged-bin.js` 启动同一 JSON-RPC Runtime。该载体不在发行包中，需从本地 checkout 构建。
- SDK 线协议（`packages/sdk/protocol`）只有 `initialize`、`session/prompt`、`shutdown` 三个请求方法，以及 `session.event`、`session.status`、`subagent.started`、`subagent.finished` 四个通知；**标准协议没有 `session/cancel` 或审批请求通道**。协议 README 同时明确：客户端放弃一个 turn 只能关闭 Runtime 进程（无 cancel/session-close 方法）；server→client 请求是 dead capability，标准 SDK 通道无法承载工具级审批。

## Windows 路径决策（已确认 2026-08-23）

1. 首选：保留“LumiMate Python Runtime → Python SDK → JSON-RPC stdio → Harness Runtime”拓扑；在 Windows 上通过构建 dev `node` 载体并以 `DSH_RUNTIME_MODE=node` 启动，Python SDK 客户端不变（用户 2026-08-23 已确认：A 优先、B 兜底）。
2. 若 dev 载体构建或运行验证失败：切换到 Node sidecar 回退方案（运行时由独立 Node 进程启动，Bridge 适配层不变）。
3. 适配层只依赖公开 SDK API 与线协议（`DeepSeekHarness`/`HarnessClient`/协议类型），不依赖 Harness 私有内部实现，保证后续可替换或独立服务化。

## Consequences

- 首个 Spike 必须先在 Windows 上验证“Python SDK + dev node 载体”能完成一次受控任务；这是 0001 拓扑的硬前提。
- 标准线协议无取消与审批通道：取消/暂停按协作式步骤边界语义实现；工具级审批需要 LumiMate 侧策略层，具体通道以 Spike 验证为准：先试 ACP，失败再自研 cordis 插件（见升级提案 §13）。
- LumiMate 必须维护可替换的 Bridge 适配层，不绑定 Harness developer preview 的私有内部实现。


## Spike 验证结论（2026-08-23，T2 实测）

- Windows「Python SDK + dev node 载体」成立：构建 dev node 闭包（vendor 构建脚本在 Windows 上 spawn pnpm.cmd 报 EINVAL，按脚本等价步骤手动 deploy + 修复闭包，脚本见 `.scratch/agent-upgrade/spike/repair-node-carrier.mjs`）；仓库 keyless smoke（`sdk-default`）通过；真实受控任务双 turn 均 `finish_reason=completed`，同一 `sessionId` 续跑成功。
- 审批闭环：先试 ACP 的结论——ACP 的 `session/request_permission` 只应答 ACP 自有 agent，且 ACP 仅支持 fresh sessions（无恢复），与 Session 恢复要求冲突，故回退自研 cordis 插件（`lumimate-approval-bridge`：`approval/request` → outbox ask 文件 → LumiMate 写入 inbox 决定 → `allowed-once`，超时 fail-closed）。Spike 实测 2 次 `write` 工具问询闭环（`approval/asked` → `approval/decided`）。
- 版本锁定：SDK 与 runtime-bin 均 `0.0.0.dev0`（同 checkout commit `47f943859b`，rc.5），锁定记录见 `requirements-harness.txt`；包管理已切换为 uv。
