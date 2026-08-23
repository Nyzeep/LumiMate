"""Agent 事件投影：提案 §8 的事件类型、必填字段与状态转换事件映射。"""

from __future__ import annotations

from typing import Any, FrozenSet, Mapping

from .state_machine import TaskState, apply_transition


class AgentEventError(ValueError):
    """事件类型或必填字段不合法。"""


TASK_EVENT_TYPES: FrozenSet[str] = frozenset(
    {
        "agent.task.created",
        "agent.task.planning",
        "agent.task.awaiting_plan_approval",
        "agent.task.running",
        "agent.task.awaiting_permission",
        "agent.task.tool_started",
        "agent.task.tool_finished",
        "agent.task.file_changed",
        "agent.task.test_result",
        "agent.task.paused",
        "agent.task.cancelled",
        "agent.task.completed",
        "agent.task.failed",
    }
)

SESSION_EVENT_TYPES: FrozenSet[str] = frozenset({"agent.session.updated"})
MEMORY_EVENT_TYPES: FrozenSet[str] = frozenset({"agent.memory.proposed"})

ALL_AGENT_EVENT_TYPES: FrozenSet[str] = frozenset(
    TASK_EVENT_TYPES | SESSION_EVENT_TYPES | MEMORY_EVENT_TYPES
)

REQUIRED_FIELDS: Mapping[str, FrozenSet[str]] = {
    "agent.task.created": frozenset({"taskId", "title", "state"}),
    "agent.task.planning": frozenset({"taskId"}),
    "agent.task.awaiting_plan_approval": frozenset({"taskId", "plan"}),
    "agent.task.running": frozenset({"taskId"}),
    "agent.task.awaiting_permission": frozenset({"taskId", "requestId", "category"}),
    "agent.task.tool_started": frozenset({"taskId", "toolName", "callId", "status"}),
    "agent.task.tool_finished": frozenset({"taskId", "toolName", "callId", "status"}),
    "agent.task.file_changed": frozenset({"taskId", "path", "operation"}),
    "agent.task.test_result": frozenset({"taskId", "command", "passed", "failed", "durationMs"}),
    "agent.task.paused": frozenset({"taskId"}),
    "agent.task.cancelled": frozenset({"taskId"}),
    "agent.task.completed": frozenset({"taskId"}),
    "agent.task.failed": frozenset({"taskId"}),
    "agent.session.updated": frozenset({"sessionId", "status", "summary"}),
    "agent.memory.proposed": frozenset({"proposalId", "summary", "kind"}),
}

# 提案 §9 允许转换 → §8 事件类型；无对应 §8 事件的转换（running -> cancelling）不在表中。
EVENT_TYPE_FOR_TRANSITION: Mapping[tuple[TaskState, TaskState], str] = {
    (TaskState.DRAFT, TaskState.PLANNING): "agent.task.planning",
    (TaskState.PLANNING, TaskState.AWAITING_PLAN_APPROVAL): "agent.task.awaiting_plan_approval",
    (TaskState.PLANNING, TaskState.FAILED): "agent.task.failed",
    (TaskState.PLANNING, TaskState.CANCELLED): "agent.task.cancelled",
    (TaskState.AWAITING_PLAN_APPROVAL, TaskState.RUNNING): "agent.task.running",
    (TaskState.AWAITING_PLAN_APPROVAL, TaskState.CANCELLED): "agent.task.cancelled",
    (TaskState.AWAITING_PERMISSION, TaskState.RUNNING): "agent.task.running",
    (TaskState.AWAITING_PERMISSION, TaskState.CANCELLED): "agent.task.cancelled",
    (TaskState.AWAITING_PERMISSION, TaskState.PAUSED): "agent.task.paused",
    (TaskState.RUNNING, TaskState.AWAITING_PERMISSION): "agent.task.awaiting_permission",
    (TaskState.RUNNING, TaskState.PAUSED): "agent.task.paused",
    (TaskState.RUNNING, TaskState.COMPLETED): "agent.task.completed",
    (TaskState.RUNNING, TaskState.FAILED): "agent.task.failed",
    (TaskState.CANCELLING, TaskState.CANCELLED): "agent.task.cancelled",
    (TaskState.CANCELLING, TaskState.FAILED): "agent.task.failed",
    (TaskState.PAUSED, TaskState.RUNNING): "agent.task.running",
    (TaskState.PAUSED, TaskState.CANCELLED): "agent.task.cancelled",
}


def build_agent_event(
    event_type: str,
    task_id: str | None = None,
    session_id: str | None = None,
    **fields: Any,
) -> dict[str, Any]:
    """构造 §8 事件 payload；非法类型或缺失必填字段时拒绝。"""
    if event_type not in ALL_AGENT_EVENT_TYPES:
        raise AgentEventError(f"未知的 Agent 事件类型：{event_type}")

    payload: dict[str, Any] = {"type": event_type}
    if task_id is not None:
        payload["taskId"] = task_id
    if session_id is not None:
        payload["sessionId"] = session_id
    payload.update(fields)

    missing = [name for name in sorted(REQUIRED_FIELDS[event_type]) if payload.get(name) is None]
    if missing:
        raise AgentEventError(
            f"事件 {event_type} 缺少必填字段：{', '.join(missing)}"
        )
    return payload


def build_transition_event(
    current: TaskState,
    target: TaskState,
    task_id: str | None = None,
    session_id: str | None = None,
    **fields: Any,
) -> dict[str, Any] | None:
    """校验状态转换并生成对应的 §8 事件；无对应事件的转换返回 None。"""
    apply_transition(current, target)
    event_type = EVENT_TYPE_FOR_TRANSITION.get((current, target))
    if event_type is None:
        return None
    return build_agent_event(
        event_type,
        task_id=task_id,
        session_id=session_id,
        **fields,
    )
