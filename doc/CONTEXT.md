# LumiMate

LumiMate 是一个本地优先的桌面 AI Companion：以人格、声音、情绪和空间表现为核心，同时具备可控、可审计、可恢复的 Agent 任务执行能力。

## 角色与边界

**Companion**:
LumiMate 的人格与陪伴层，负责对话、ASR/TTS、情绪与空间表现，以及任务开始、审批、完成和失败的表达。
_Avoid_: 聊天窗口、前端、Lumi

**Task Agent**:
由 DeepSeek Harness 驱动的任务执行层，负责代码理解、计划、工具调用、测试执行与结果汇总。
_Avoid_: 后端 Agent、执行器

**Bridge**:
Companion 与 Task Agent 之间唯一的适配层，负责启动/关闭 Harness、创建/恢复 Session、映射任务状态、转发权限请求与同步 UI。
_Avoid_: 中间件、网关

**Workspace**:
Task Agent 允许操作的任务工作根目录；第一阶段固定为 `D:\LumiMate`。
_Avoid_: 项目根、沙箱

## 任务执行

**Task**:
用户交办、由 Task Agent 执行的一次受控开发任务，拥有独立状态机与生命周期。
_Avoid_: 请求、Job

**Task State**:
任务的公开生命周期状态：规划、等待计划确认、等待权限、运行、暂停、取消中、已取消、已完成、失败。
_Avoid_: 阶段、模式

**Session**:
一次 Task Agent 工作的完整可恢复上下文；Harness Session 是 Agent 执行事实的主要来源。
_Avoid_: 对话记录、Thread

**Plan**:
Task Agent 执行前生成、并经用户确认的执行计划。
_Avoid_: 大纲、步骤说明

**Todo**:
Plan 分解出的可跟踪待办步骤。
_Avoid_: 子任务、检查项

## 权限

**Permission Level**:
按风险划分的操作权限等级：Low（自动执行）、Medium（任务内确认后连续执行）、High（每次确认）。
_Avoid_: 权限级别、角色

**Grant**:
对 Medium 操作的授权，必须绑定当前 Task、固定 Workspace、明确操作范围和当前 Session，并在任务结束时失效。
_Avoid_: 信任、放行

**Approval**:
用户对计划或中/高风险操作的确权动作；情绪、关系、时长或历史成功率不得自动提升权限。
_Avoid_: 同意、批准流程

## 记忆与呈现

**Memory**:
仅保存用户明确允许保存的长期摘要，经过“Agent 提议 → 用户确认 → LumiMate 保存”三步。
_Avoid_: 历史记录、知识库

**Projection**:
LumiMate 为 UI 保存的 Session 摘要投影（状态、标题、摘要、最近结果），而非完整 Harness 事件日志。
_Avoid_: 缓存、事件副本

## 界面

**Scene（场景）**:
LumiMate 的顶层界面单元（首页、对话、陪伴、工作台、设置等）；所有场景常驻同屏、切换显隐，不存在路由跳转。
_Avoid_: 页面、路由

**Subspace（子空间）**:
工作台内部互斥的三个分区：核心舱（模型加载与管理）、星系选择（模型下载）、任务舱（Task 执行与审批）。
_Avoid_: 标签页、子页面

## 执行基础设施

**载体（Runtime Carrier）**:
Harness Runtime 的运行形态（官方 exe 载体或 dev-only node 载体）；Windows 无官方载体，需构建 node 载体或改用 Node sidecar。
_Avoid_: 运行时、二进制

**Turn**:
Harness 一次从用户输入到回应的完整执行周期；Session 恢复点以最近一次 turn（idle）边界为准。
_Avoid_: 轮次、回合
