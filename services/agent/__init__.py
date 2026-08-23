"""LumiMate Agent 子系统：Task 状态机、事件投影、模型与持久化。"""

from .events import (
    ALL_AGENT_EVENT_TYPES,
    MEMORY_EVENT_TYPES,
    SESSION_EVENT_TYPES,
    TASK_EVENT_TYPES,
    AgentEventError,
    build_agent_event,
    build_transition_event,
)

from .models import Grant, SessionProjection, Task
from .service import AgentService
from .state_machine import (
    IllegalTransitionError,
    TERMINAL_STATES,
    TaskState,
    apply_transition,
    can_transition,
)
from .store import TaskStore

__all__ = [
    "ALL_AGENT_EVENT_TYPES",
    "AgentEventError",
    "AgentService",
    "MEMORY_EVENT_TYPES",
    "SESSION_EVENT_TYPES",
    "TASK_EVENT_TYPES",
    "Grant",
    "SessionProjection",
    "Task",
    "TaskStore",
    "IllegalTransitionError",
    "TERMINAL_STATES",
    "TaskState",
    "apply_transition",
    "build_agent_event",
    "build_transition_event",
    "can_transition",
]

