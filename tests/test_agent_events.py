import pytest

from services.agent.events import (
    AgentEventError,
    build_agent_event,
    build_transition_event,
)
from services.agent.state_machine import IllegalTransitionError, TaskState


def test_task_created_payload_shape():
    event = build_agent_event(
        "agent.task.created",
        task_id="t1",
        title="修复测试失败",
        state="planning",
    )
    assert event == {
        "type": "agent.task.created",
        "taskId": "t1",
        "title": "修复测试失败",
        "state": "planning",
    }


def test_awaiting_permission_payload_shape():
    event = build_agent_event(
        "agent.task.awaiting_permission",
        task_id="t1",
        session_id="s1",
        requestId="req-1",
        category="file_modify",
        toolName="edit_file",
        details={"path": "src/a.py"},
    )
    assert event == {
        "type": "agent.task.awaiting_permission",
        "taskId": "t1",
        "sessionId": "s1",
        "requestId": "req-1",
        "category": "file_modify",
        "toolName": "edit_file",
        "details": {"path": "src/a.py"},
    }


def test_session_updated_requires_session_id():
    event = build_agent_event(
        "agent.session.updated",
        task_id="t1",
        session_id="s1",
        status="idle",
        summary="计划已生成",
    )
    assert event["type"] == "agent.session.updated"
    assert event["sessionId"] == "s1"
    assert event["taskId"] == "t1"
    assert event["status"] == "idle"
    assert event["summary"] == "计划已生成"


def test_memory_proposed_payload_shape():
    event = build_agent_event(
        "agent.memory.proposed",
        proposalId="p1",
        summary="用户偏好使用 pytest",
        kind="preference",
    )
    assert event == {
        "type": "agent.memory.proposed",
        "proposalId": "p1",
        "summary": "用户偏好使用 pytest",
        "kind": "preference",
    }


def test_task_event_without_task_id_is_rejected():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.created", title="缺 taskId")


def test_session_event_without_session_id_is_rejected():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.session.updated", status="idle", summary="缺 sessionId")


def test_memory_event_without_proposal_id_is_rejected():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.memory.proposed", summary="缺 proposalId", kind="preference")


def test_unknown_event_type_is_rejected():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.nope", task_id="t1")


def test_extra_fields_pass_through():
    event = build_agent_event(
        "agent.task.completed",
        task_id="t1",
        session_id="s1",
        result={"filesChanged": 3, "testsPassed": 12},
    )
    assert event["result"] == {"filesChanged": 3, "testsPassed": 12}

def test_created_requires_title_and_state():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.created", task_id="t1", title="缺 state")
    event = build_agent_event("agent.task.created", task_id="t1", title="完整", state="draft")
    assert event["state"] == "draft"


def test_awaiting_plan_approval_requires_plan():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.awaiting_plan_approval", task_id="t1")
    event = build_agent_event(
        "agent.task.awaiting_plan_approval",
        task_id="t1",
        plan=[{"step": "读代码"}],
    )
    assert event["plan"] == [{"step": "读代码"}]


def test_awaiting_permission_requires_request_and_category():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.awaiting_permission", task_id="t1", category="file_modify")
    event = build_agent_event(
        "agent.task.awaiting_permission",
        task_id="t1",
        requestId="req-1",
        category="file_modify",
    )
    assert event["requestId"] == "req-1"


def test_tool_started_requires_tool_fields():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.tool_started", task_id="t1", callId="c1", status="running")
    event = build_agent_event(
        "agent.task.tool_started",
        task_id="t1",
        toolName="read_file",
        callId="c1",
        status="running",
    )
    assert event["toolName"] == "read_file"


def test_file_changed_requires_path_and_operation():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.file_changed", task_id="t1", path="a.py")
    event = build_agent_event(
        "agent.task.file_changed",
        task_id="t1",
        path="a.py",
        operation="modify",
    )
    assert event["operation"] == "modify"


def test_test_result_requires_command_and_counts():
    with pytest.raises(AgentEventError):
        build_agent_event("agent.task.test_result", task_id="t1", command="pytest", passed=1, failed=0)
    event = build_agent_event(
        "agent.task.test_result",
        task_id="t1",
        command="pytest",
        passed=1,
        failed=0,
        durationMs=123,
    )
    assert event["command"] == "pytest"


@pytest.mark.parametrize(
    "current,target,expected_type",
    [
        (TaskState.DRAFT, TaskState.PLANNING, "agent.task.planning"),
        (TaskState.PLANNING, TaskState.FAILED, "agent.task.failed"),
        (TaskState.PLANNING, TaskState.CANCELLED, "agent.task.cancelled"),
        (TaskState.AWAITING_PLAN_APPROVAL, TaskState.RUNNING, "agent.task.running"),
        (TaskState.AWAITING_PLAN_APPROVAL, TaskState.CANCELLED, "agent.task.cancelled"),
        (TaskState.AWAITING_PERMISSION, TaskState.RUNNING, "agent.task.running"),
        (TaskState.AWAITING_PERMISSION, TaskState.CANCELLED, "agent.task.cancelled"),
        (TaskState.AWAITING_PERMISSION, TaskState.PAUSED, "agent.task.paused"),
        (TaskState.RUNNING, TaskState.PAUSED, "agent.task.paused"),
        (TaskState.RUNNING, TaskState.COMPLETED, "agent.task.completed"),
        (TaskState.RUNNING, TaskState.FAILED, "agent.task.failed"),
        (TaskState.CANCELLING, TaskState.CANCELLED, "agent.task.cancelled"),
        (TaskState.CANCELLING, TaskState.FAILED, "agent.task.failed"),
        (TaskState.PAUSED, TaskState.RUNNING, "agent.task.running"),
        (TaskState.PAUSED, TaskState.CANCELLED, "agent.task.cancelled"),
    ],
)
def test_build_transition_event_maps_allowed_transitions(current, target, expected_type):
    event = build_transition_event(current, target, task_id="t1")
    assert event is not None
    assert event["type"] == expected_type
    assert event["taskId"] == "t1"



def test_planning_to_awaiting_plan_approval_event_includes_plan():
    event = build_transition_event(
        TaskState.PLANNING,
        TaskState.AWAITING_PLAN_APPROVAL,
        task_id="t1",
        plan=[{"step": "读代码"}],
    )
    assert event["type"] == "agent.task.awaiting_plan_approval"
    assert event["plan"] == [{"step": "读代码"}]


def test_running_to_awaiting_permission_event_includes_request():
    event = build_transition_event(
        TaskState.RUNNING,
        TaskState.AWAITING_PERMISSION,
        task_id="t1",
        requestId="req-1",
        category="file_modify",
    )
    assert event["type"] == "agent.task.awaiting_permission"
    assert event["category"] == "file_modify"

def test_running_to_cancelling_has_no_section8_event():
    assert build_transition_event(TaskState.RUNNING, TaskState.CANCELLING, task_id="t1") is None


def test_build_transition_event_rejects_forbidden_transition():
    with pytest.raises(IllegalTransitionError):
        build_transition_event(TaskState.DRAFT, TaskState.RUNNING, task_id="t1")




def test_required_fields_cover_every_event_type():
    from services.agent.events import ALL_AGENT_EVENT_TYPES, REQUIRED_FIELDS

    assert set(REQUIRED_FIELDS) == set(ALL_AGENT_EVENT_TYPES)


def test_every_allowed_transition_has_event_or_is_explicitly_eventless():
    from services.agent.events import EVENT_TYPE_FOR_TRANSITION
    from services.agent.state_machine import ALLOWED_TRANSITIONS

    covered = set(EVENT_TYPE_FOR_TRANSITION) | {(TaskState.RUNNING, TaskState.CANCELLING)}
    allowed = {
        (current, target)
        for current, targets in ALLOWED_TRANSITIONS.items()
        for target in targets
    }
    assert covered == allowed
