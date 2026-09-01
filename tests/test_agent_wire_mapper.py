from services.agent.bridge.wire_mapper import (
    map_run_result,
    map_session_event,
    map_session_status,
    map_subagent_notification,
)


def test_tool_call_event_maps_to_tool_started():
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "tool/call",
            "data": {"turn": 1, "step": 1, "callId": "call-1", "name": "write", "arguments": "{}"},
        },
    }
    events = map_session_event(wire, task_id="t1")
    assert events == [
        {
            "type": "agent.task.tool_started",
            "taskId": "t1",
            "sessionId": "s1",
            "toolName": "write",
            "callId": "call-1",
            "status": "running",
            "arguments": "arguments omitted for privacy",
        }
    ]


def test_tool_call_does_not_project_raw_arguments():
    raw_arguments = "token=not-for-projection; content=private-input"
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "tool/call",
            "data": {"callId": "call-1", "name": "write", "arguments": raw_arguments},
        },
    }

    event = map_session_event(wire, task_id="t1")[0]

    assert event["arguments"] == "arguments omitted for privacy"
    assert raw_arguments not in str(event)


def test_tool_result_event_maps_to_tool_finished_ok():
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "tool/result",
            "data": {
                "callId": "call-1",
                "message": {"content": [{"type": "text", "text": "ok"}]},
            },
        },
    }
    events = map_session_event(wire, task_id="t1")
    assert events == [
        {
            "type": "agent.task.tool_finished",
            "taskId": "t1",
            "sessionId": "s1",
            "toolName": "unknown",
            "callId": "call-1",
            "status": "ok",
        }
    ]


def test_tool_result_with_error_maps_to_tool_finished_error():
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "tool/result",
            "data": {"callId": "call-1", "error": {"name": "ToolError"}},
        },
    }
    events = map_session_event(wire, task_id="t1")
    assert events[0]["status"] == "error"


def test_malformed_session_event_maps_to_nothing():
    assert map_session_event({"sessionId": "s1", "event": "not-a-mapping"}, task_id="t1") == []
    assert map_session_event({"sessionId": "s1", "event": {"type": "tool/call", "data": "not-a-mapping"}}, task_id="t1") == []


def test_turn_end_completed_maps_to_completed():
    wire = {
        "sessionId": "s1",
        "event": {"type": "turn/end", "data": {"turn": 1, "reason": {"kind": "completed"}}},
    }
    events = map_session_event(wire, task_id="t1")
    assert events == [
        {"type": "agent.task.completed", "taskId": "t1", "sessionId": "s1"}
    ]


def test_turn_end_error_maps_to_failed():
    wire = {
        "sessionId": "s1",
        "event": {"type": "turn/end", "data": {"turn": 1, "reason": {"kind": "error"}}},
    }
    events = map_session_event(wire, task_id="t1")
    assert events[0]["type"] == "agent.task.failed"
    assert events[0]["failure"] == {"reason": "error"}


def test_turn_end_auth_error_preserves_a_redacted_failure_signal():
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "turn/end",
            "data": {
                "reason": {
                    "kind": "error",
                    "error": {
                        "message": "Authentication failed for api key: sk-test-credential",
                        "code": "AUTH",
                        "status": 401,
                    },
                }
            },
        },
    }

    events = map_session_event(wire, task_id="t1")

    assert events[0]["failure"] == {
        "reason": "AUTH",
        "status": 401,
        "message": "Authentication failed (HTTP 401)",
    }


def test_turn_end_error_does_not_project_raw_provider_text():
    raw_provider_message = "token=unrecognized-secret; Authorization: bearer-value; https://gateway.test/?credential=query-value"
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "turn/end",
            "data": {
                "reason": {
                    "kind": "error",
                    "error": {
                        "message": raw_provider_message,
                        "code": "AUTH",
                        "status": 401,
                    },
                }
            },
        },
    }

    failure = map_session_event(wire, task_id="t1")[0]["failure"]

    assert failure == {
        "reason": "AUTH",
        "status": 401,
        "message": "Authentication failed (HTTP 401)",
    }
    assert raw_provider_message not in str(failure)


def test_turn_end_error_does_not_project_untrusted_provider_code():
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "turn/end",
            "data": {
                "reason": {
                    "kind": "error",
                    "error": {
                        "message": "unexpected provider failure",
                        "code": "SECRET_TOKEN",
                        "status": 500,
                    },
                }
            },
        },
    }

    failure = map_session_event(wire, task_id="t1")[0]["failure"]

    assert failure == {
        "reason": "HTTP_5XX",
        "status": 500,
        "message": "Harness request failed (HTTP 500)",
    }


def test_irrelevant_events_map_to_nothing():
    for event_type in ("turn/start", "step/start", "step/end", "assistant/message", "user/message"):
        wire = {"sessionId": "s1", "event": {"type": event_type, "data": {}}}
        assert map_session_event(wire, task_id="t1") == []


def test_session_status_running_maps_to_session_updated():
    event = map_session_status("s1", "running", task_id="t1")
    assert event == {
        "type": "agent.session.updated",
        "taskId": "t1",
        "sessionId": "s1",
        "status": "running",
        "summary": "",
    }


def test_session_status_idle_maps_to_session_updated():
    event = map_session_status("s1", "idle", task_id="t1")
    assert event is not None
    assert event["status"] == "idle"


def test_run_result_completed_maps_to_completed_event():
    class FakeResult:
        finish_reason = "completed"

    events = map_run_result(FakeResult(), task_id="t1", session_id="s1")
    assert events == [
        {"type": "agent.task.completed", "taskId": "t1", "sessionId": "s1"}
    ]


def test_unknown_terminal_run_result_maps_to_failed_event():
    class FakeResult:
        finish_reason = "interrupted"

    events = map_run_result(FakeResult(), task_id="t1", session_id="s1")

    assert events == [
        {
            "type": "agent.task.failed",
            "taskId": "t1",
            "sessionId": "s1",
            "failure": {"reason": "error"},
        }
    ]


def test_run_result_error_maps_to_failed_event():
    class FakeResult:
        finish_reason = "error"

    events = map_run_result(FakeResult(), task_id="t1", session_id="s1")
    assert events[0]["type"] == "agent.task.failed"


def test_run_result_without_terminal_reason_maps_to_failed_event():
    class FakeResult:
        finish_reason = None

    events = map_run_result(FakeResult(), task_id="t1", session_id="s1")

    assert events[0]["type"] == "agent.task.failed"
    assert events[0]["failure"] == {"reason": "error"}


def test_subagent_started_notification_maps_to_nothing():
    assert (
        map_subagent_notification(
            {"parentSessionId": "s1", "childSessionId": "s2"}, task_id="t1"
        )
        == []
    )


def test_subagent_finished_notification_maps_to_nothing():
    assert (
        map_subagent_notification(
            {"parentSessionId": "s1", "childSessionId": "s2", "status": "ok"},
            task_id="t1",
        )
        == []
    )

