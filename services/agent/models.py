"""Task / SessionProjection / Grant 领域模型。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .state_machine import TaskState


@dataclass
class Grant:
    """Medium 权限授权：taskId + sessionId + workspace + category 四元组。"""

    task_id: str
    session_id: str
    workspace: str
    category: str


@dataclass
class Task:
    """一次受控开发任务的投影模型。"""

    id: str
    title: str
    state: TaskState
    workspace: str = ""
    goal: str = ""
    session_id: str | None = None
    plan: list[dict[str, Any]] | None = None
    summary: str = ""
    result: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    interrupted: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["state"] = self.state.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Task:
        data = dict(payload)
        data["state"] = TaskState(data["state"])
        return cls(**data)


@dataclass
class SessionProjection:
    """LumiMate 保存的 Session 摘要投影，而非完整 Harness 事件日志。"""

    session_id: str
    status: str
    task_id: str | None = None
    title: str = ""
    summary: str = ""
    last_result: dict[str, Any] | None = None
    resume_index: dict[str, Any] | None = None
