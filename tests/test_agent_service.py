from pathlib import Path

import pytest

from services.agent.service import AgentService
from services.agent.state_machine import TaskState
from services.agent.store import TaskStore


WORKSPACE = r"D:\LumiMate"


class FakeBridge:
    def __init__(self) -> None:
        self.runs: list[tuple[str, str, str]] = []
        self.cancelled: list[str] = []
        self.closed = False
        self.last_results: dict[str, object] = {}

    def run_task(self, session_id: str, task_id: str, goal: str) -> None:
        self.runs.append((session_id, task_id, goal))

    def cancel(self, session_id: str) -> str:
        self.cancelled.append(session_id)
        return "cancelled"

    def last_result(self, session_id: str):
        return self.last_results.get(session_id)

    def close(self) -> None:
        self.closed = True


def make_service(tmp_path: Path) -> tuple[AgentService, FakeBridge, list[dict]]:
    bridge = FakeBridge()
    published: list[dict] = []
    service = AgentService(
        store=TaskStore(tmp_path / "tasks"),
        sessions_root=tmp_path / "sessions",
        bridge=bridge,
        publisher=published.append,
        workspace=WORKSPACE,
    )
    return service, bridge, published


def complete_plan(service: AgentService, bridge: FakeBridge, task) -> None:
    bridge.last_results[task.session_id] = type(
        "Result", (), {"final_response": "计划：1. 读代码 2. 写测试"}
    )()
    service.on_bridge_event(
        {
            "type": "agent.task.completed",
            "taskId": task.id,
            "sessionId": task.session_id,
        }
    )


def test_start_task_creates_planning_task_and_runs_plan_turn(tmp_path):
    service, bridge, published = make_service(tmp_path)

    task = service.start_task(title="修复测试", goal="让 pytest 全绿", workspace=WORKSPACE)

    assert task.state == TaskState.PLANNING
    assert task.workspace == WORKSPACE
    assert bridge.runs == [(task.session_id, task.id, "让 pytest 全绿")]
    assert any(e["type"] == "agent.task.created" for e in published)
    assert any(e["type"] == "agent.task.planning" for e in published)


def test_start_task_rejects_foreign_workspace(tmp_path):
    service, _, _ = make_service(tmp_path)
    with pytest.raises(ValueError):
        service.start_task(title="越权", goal="x", workspace=r"C:\Other")


def test_plan_completion_moves_to_awaiting_plan_approval(tmp_path):
    service, bridge, published = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)

    complete_plan(service, bridge, task)

    current = service.get_task(task.id)
    assert current.state == TaskState.AWAITING_PLAN_APPROVAL
    assert current.plan == [{"summary": "计划：1. 读代码 2. 写测试"}]
    assert any(e["type"] == "agent.task.awaiting_plan_approval" for e in published)


def test_approve_plan_starts_execution(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)

    service.approve_plan(task.id, approve=True)

    current = service.get_task(task.id)
    assert current.state == TaskState.RUNNING
    assert bridge.runs[-1] == (task.session_id, task.id, "g")


def test_reject_plan_cancels_task(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)

    service.approve_plan(task.id, approve=False)

    assert service.get_task(task.id).state == TaskState.CANCELLED


def test_running_completion_marks_completed(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)

    service.on_bridge_event(
        {
            "type": "agent.task.completed",
            "taskId": task.id,
            "sessionId": task.session_id,
        }
    )

    assert service.get_task(task.id).state == TaskState.COMPLETED


def test_pause_cancels_bridge_and_becomes_paused(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)

    service.pause_task(task.id)
    assert service.get_task(task.id).state == TaskState.PAUSED
    assert bridge.cancelled == [task.session_id]

    service.on_bridge_event(
        {
            "type": "agent.task.cancelled",
            "taskId": task.id,
            "sessionId": task.session_id,
        }
    )
    assert service.get_task(task.id).state == TaskState.PAUSED


def test_resume_runs_again(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.pause_task(task.id)

    service.resume_task(task.id)

    assert service.get_task(task.id).state == TaskState.RUNNING
    assert bridge.runs[-1] == (task.session_id, task.id, "g")


def test_failure_event_marks_failed(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)

    service.on_bridge_event(
        {
            "type": "agent.task.failed",
            "taskId": task.id,
            "sessionId": task.session_id,
            "failure": {"reason": "error"},
        }
    )

    assert service.get_task(task.id).state == TaskState.FAILED


def test_cancel_task_marks_cancelled(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)

    service.cancel_task(task.id)

    assert service.get_task(task.id).state == TaskState.CANCELLED
    assert bridge.cancelled == [task.session_id]


def test_status_shape(tmp_path):
    service, _, _ = make_service(tmp_path)
    status = service.status()
    assert status["ready"] is True
    assert status["harnessAvailable"] is True
    assert status["currentTask"] is None
    assert status["sessions"] == []


def test_resume_session_reuses_provided_session_id(tmp_path):
    service, bridge, _ = make_service(tmp_path)

    task = service.resume_session(
        session_id="s-existing",
        title="续跑任务",
        goal="继续执行",
        workspace=WORKSPACE,
    )

    assert task.session_id == "s-existing"
    assert task.state == TaskState.PLANNING
    assert bridge.runs[-1] == ("s-existing", task.id, "继续执行")

