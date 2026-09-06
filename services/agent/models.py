"""Task / SessionProjection / Grant 领域模型。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .state_machine import TaskState, apply_transition


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

    def transition_to(self, target: TaskState) -> TaskState:
        """校验并推进 Task State（提案 §9 转换表）；非法转换抛 IllegalTransitionError。"""
        apply_transition(self.state, target)
        self.state = target
        return self.state

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["state"] = self.state.value
        return payload

    def to_api_dict(self) -> dict[str, Any]:
        """HTTP API 使用的 camelCase 投影（§7 字段风格）。"""
        return {
            "taskId": self.id,
            "title": self.title,
            "state": self.state.value,
            "workspace": self.workspace,
            "goal": self.goal,
            "sessionId": self.session_id,
            "plan": self.plan,
            "summary": self.summary,
            "result": self.result,
            "failure": self.failure,
            "interrupted": self.interrupted,
        }

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

