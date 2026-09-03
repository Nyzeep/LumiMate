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
        self.approval_answers: list[tuple[str, str, bool]] = []

    def run_task(self, session_id: str, task_id: str, goal: str) -> None:
        self.runs.append((session_id, task_id, goal))

    def cancel(self, session_id: str) -> str:
        self.cancelled.append(session_id)
        return "cancelled"

    def last_result(self, session_id: str):
        return self.last_results.get(session_id)

    def answer_approval(self, session_id: str, request_id: str, approve: bool) -> None:
        self.approval_answers.append((session_id, request_id, approve))
        return self.last_results.get(session_id)

    def close(self) -> None:
        self.closed = True


def make_service(tmp_path: Path, with_stores: bool = False) -> tuple[AgentService, FakeBridge, list[dict]]:
    from services.agent.memory import MemoryStore
    from services.agent.persistence import ProjectionStore

    bridge = FakeBridge()
    published: list[dict] = []
    service = AgentService(
        store=TaskStore(tmp_path / "tasks"),
        sessions_root=tmp_path / "sessions",
        bridge=bridge,
        publisher=published.append,
        workspace=WORKSPACE,
        projections=ProjectionStore(tmp_path / "projections") if with_stores else None,
        memory=MemoryStore(tmp_path / "memory") if with_stores else None,
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



def tool_started(task, tool_name="write", call_id="call-1", arguments='{"file_path": "D:\\\\LumiMate\\\\a.py"}'):
    return {
        "type": "agent.task.tool_started",
        "taskId": task.id,
        "sessionId": task.session_id,
        "toolName": tool_name,
        "callId": call_id,
        "arguments": arguments,
    }


def test_tool_without_grant_moves_to_awaiting_permission(tmp_path):
    service, bridge, published = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)

    service.on_bridge_event(tool_started(task))

    assert service.get_task(task.id).state == TaskState.AWAITING_PERMISSION
    awaiting = next(
        e for e in published if e["type"] == "agent.task.awaiting_permission"
    )
    assert awaiting["requestId"] == "call-1"
    assert awaiting["category"] == "file_modify"
    assert not any(e["type"] == "agent.task.tool_started" for e in published)


def test_approve_permission_grants_medium_and_resumes(tmp_path):
    service, bridge, published = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task))

    service.approve_permission(
        task.id, request_id="call-1", grant_category="file_modify", approve=True
    )

    assert service.get_task(task.id).state == TaskState.RUNNING
    assert bridge.approval_answers == [(task.session_id, "call-1", True)]
    tool_event = next(e for e in published if e["type"] == "agent.task.tool_started")
    assert tool_event["arguments"] == "arguments omitted for privacy"


def test_second_same_category_tool_after_grant_allows(tmp_path):
    service, bridge, published = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task, call_id="call-1"))
    service.approve_permission(
        task.id, request_id="call-1", grant_category="file_modify", approve=True
    )

    published.clear()
    service.on_bridge_event(tool_started(task, call_id="call-2"))

    assert service.get_task(task.id).state == TaskState.RUNNING
    assert any(e["type"] == "agent.task.tool_started" for e in published)


def test_approve_permission_reject_cancels_task(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task))

    service.approve_permission(
        task.id, request_id="call-1", grant_category="file_modify", approve=False
    )

    assert service.get_task(task.id).state == TaskState.CANCELLED
    assert bridge.approval_answers == [(task.session_id, "call-1", False)]


def test_cancel_task_revokes_existing_grants(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task))
    service.approve_permission(
        task.id, request_id="call-1", grant_category="file_modify", approve=True
    )

    service.cancel_task(task.id)

    assert service._policy.check(
        task_id=task.id,
        session_id=task.session_id,
        workspace=WORKSPACE,
        action="write",
    )[1] == "ask"


def test_pause_keeps_grants_for_the_same_task(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task))
    service.approve_permission(
        task.id, request_id="call-1", grant_category="file_modify", approve=True
    )

    service.pause_task(task.id)
    service.on_bridge_event(
        {
            "type": "agent.task.cancelled",
            "taskId": task.id,
            "sessionId": task.session_id,
        }
    )

    assert service.get_task(task.id).state == TaskState.PAUSED
    assert service._policy.check(
        task_id=task.id,
        session_id=task.session_id,
        workspace=WORKSPACE,
        action="write",
    )[1] == "allow"


def test_tool_call_while_waiting_permission_is_rejected(tmp_path):
    service, bridge, published = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task, call_id="call-1"))
    published.clear()

    service.on_bridge_event(
        tool_started(
            task,
            tool_name="read",
            call_id="call-2",
            arguments='{"file_path": "../outside.py"}',
        )
    )

    assert service.get_task(task.id).state == TaskState.AWAITING_PERMISSION
    assert published[-1]["type"] == "agent.task.tool_finished"
    assert published[-1]["status"] == "error"


def test_tool_session_mismatch_is_rejected(tmp_path):
    service, bridge, published = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)

    service.on_bridge_event(
        {
            "type": "agent.task.tool_started",
            "taskId": task.id,
            "sessionId": "other-session",
            "toolName": "write",
            "callId": "call-1",
            "arguments": '{"file_path": "a.py"}',
        }
    )

    assert service.get_task(task.id).state == TaskState.RUNNING
    assert published[-1]["summary"] == "工具调用 Session 与 Task 不匹配"


def test_high_tool_always_asks_even_after_approval(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(
        tool_started(
            task,
            tool_name="write",
            call_id="call-1",
            arguments='{"file_path": "../outside.py"}',
        )
    )
    service.approve_permission(
        task.id, request_id="call-1", grant_category="file_modify", approve=True
    )

    service.on_bridge_event(
        tool_started(
            task,
            tool_name="write",
            call_id="call-2",
            arguments='{"file_path": "../outside.py"}',
        )
    )

    assert service.get_task(task.id).state == TaskState.AWAITING_PERMISSION


def test_permission_category_must_match_the_pending_tool(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task))

    with pytest.raises(ValueError, match="权限类别"):
        service.approve_permission(
            task.id,
            request_id="call-1",
            grant_category="test",
            approve=True,
        )

    assert service.get_task(task.id).state == TaskState.AWAITING_PERMISSION

def test_terminal_state_revokes_grants(tmp_path):
    service, bridge, _ = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)
    service.on_bridge_event(tool_started(task, call_id="call-1"))
    service.approve_permission(
        task.id, request_id="call-1", grant_category="file_modify", approve=True
    )
    service.on_bridge_event(
        {
            "type": "agent.task.completed",
            "taskId": task.id,
            "sessionId": task.session_id,
        }
    )

    assert service.get_task(task.id).state == TaskState.COMPLETED
    level, decision = service._policy.check(
        task_id=task.id,
        session_id=task.session_id,
        workspace=WORKSPACE,
        action="write",
    )
    assert decision == "ask"


def test_non_whitelisted_tool_is_denied_without_ask(tmp_path):
    service, bridge, published = make_service(tmp_path)
    task = service.start_task(title="t", goal="g", workspace=WORKSPACE)
    complete_plan(service, bridge, task)
    service.approve_plan(task.id, approve=True)

    service.on_bridge_event(
        {
            "type": "agent.task.tool_started",
            "taskId": task.id,
            "sessionId": task.session_id,
            "toolName": "network",
            "callId": "call-1",
            "arguments": "{}",
        }
    )

    assert service.get_task(task.id).state == TaskState.RUNNING
    denied = next(
        e for e in published if e["type"] == "agent.task.tool_finished"
    )
    assert denied["status"] == "error"
    assert not any(e["type"] == "agent.task.awaiting_permission" for e in published)



def test_restart_recovers_tasks_and_projections(tmp_path):
    service, bridge, _ = make_service(tmp_path, with_stores=True)
    task = service.start_task(title="重启任务", goal="g", workspace=WORKSPACE)
    service._save_and_publish(task, "agent.task.planning")

    restarted, _, _ = make_service(tmp_path, with_stores=True)

    recovered = restarted.get_task(task.id)
    assert recovered.state == TaskState.PAUSED
    assert recovered.interrupted is True
    assert any(s["sessionId"] == task.session_id for s in restarted.list_sessions())


def test_propose_memory_publishes_event_and_confirm_saves(tmp_path):
    service, _, published = make_service(tmp_path, with_stores=True)

    proposal = service.propose_memory("用户偏好 pytest", "preference", source_task_id="t1")

    event = next(e for e in published if e["type"] == "agent.memory.proposed")
    assert event["proposalId"] == proposal["proposalId"]
    service.confirm_memory(proposal["proposalId"], accept=True)
    assert len(service._memory.list_memories()) == 1


def test_memory_without_store_raises(tmp_path):
    service, _, _ = make_service(tmp_path)
    try:
        from services.agent.memory import MemoryError

        service.propose_memory("x", "preference")
        raise AssertionError("should have raised")
    except MemoryError:
        pass
