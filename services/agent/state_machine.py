"""Task 状态机：提案 §9 的十个状态与允许/禁止转换表。"""

from __future__ import annotations

from enum import Enum
from typing import FrozenSet, Mapping


class TaskState(str, Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    AWAITING_PLAN_APPROVAL = "awaiting_plan_approval"
    AWAITING_PERMISSION = "awaiting_permission"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


TERMINAL_STATES: FrozenSet[TaskState] = frozenset(
    {TaskState.CANCELLED, TaskState.COMPLETED, TaskState.FAILED}
)


ALLOWED_TRANSITIONS: Mapping[TaskState, FrozenSet[TaskState]] = {
    TaskState.DRAFT: frozenset({TaskState.PLANNING}),
    TaskState.AWAITING_PLAN_APPROVAL: frozenset({TaskState.RUNNING, TaskState.CANCELLED}),
    TaskState.PLANNING: frozenset(
        {TaskState.AWAITING_PLAN_APPROVAL, TaskState.FAILED, TaskState.CANCELLED}
    ),
    TaskState.AWAITING_PERMISSION: frozenset({TaskState.RUNNING, TaskState.CANCELLED, TaskState.PAUSED}),
    TaskState.RUNNING: frozenset(
        {
            TaskState.AWAITING_PERMISSION,
            TaskState.PAUSED,
            TaskState.CANCELLING,
            TaskState.COMPLETED,
            TaskState.FAILED,
        }
    ),
    TaskState.CANCELLING: frozenset({TaskState.CANCELLED, TaskState.FAILED}),
    TaskState.PAUSED: frozenset({TaskState.RUNNING, TaskState.CANCELLED}),
}


class IllegalTransitionError(ValueError):
    """目标转换不在提案 §9 允许表中。"""


def can_transition(current: TaskState, target: TaskState) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, frozenset())


def apply_transition(current: TaskState, target: TaskState) -> TaskState:
    if not can_transition(current, target):
        raise IllegalTransitionError(
            f"禁止的状态转换：{current.value} -> {target.value}"
        )
    return target
