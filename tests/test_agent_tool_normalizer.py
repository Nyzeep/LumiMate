import hashlib
import json

from services.agent.tools.normalizer import ToolProjector, parse_test_summary


def tool_call(session_id, tool_name, call_id, arguments):
    return {
        "sessionId": session_id,
        "event": {
            "type": "tool/call",
            "data": {
                "callId": call_id,
                "name": tool_name,
                "arguments": json.dumps(arguments),
            },
        },
    }


def tool_result(session_id, call_id, text="ok"):
    return {
        "sessionId": session_id,
        "event": {
            "type": "tool/result",
            "data": {
                "callId": call_id,
                "message": {"content": [{"type": "text", "text": text}]},
            },
        },
    }


def test_parse_test_summary_counts():
    assert parse_test_summary("=== 3 passed, 1 failed in 1.23s ===") == (3, 1, 1230)
    assert parse_test_summary("1 passed in 0.50s") == (1, 0, 500)
    assert parse_test_summary("1 failed in 2s") == (0, 1, 2000)
    assert parse_test_summary("no summary") == (0, 0, 0)


def test_write_create_projects_file_changed(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "new.txt"
    projector = ToolProjector(str(workspace))
    projector.on_tool_call(
        tool_call("s1", "write", "c1", {"file_path": "new.txt", "content": "hello"})
    )
    target.write_text("hello", encoding="utf-8")

    events = projector.on_tool_result(tool_result("s1", "c1"), task_id="t1")

    assert len(events) == 1
    event = events[0]
    assert event["type"] == "agent.task.file_changed"
    assert event["taskId"] == "t1"
    assert event["sessionId"] == "s1"
    assert event["path"] == str(target)
    assert event["operation"] == "create"
    assert event["afterHash"] == hashlib.sha256(b"hello").hexdigest()


def test_write_update_projects_file_changed(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "a.py"
    target.write_text("old", encoding="utf-8")
    projector = ToolProjector(str(workspace))
    projector.on_tool_call(
        tool_call("s1", "write", "c1", {"file_path": "a.py", "content": "new"})
    )
    target.write_text("new", encoding="utf-8")

    events = projector.on_tool_result(tool_result("s1", "c1"), task_id="t1")

    assert events[0]["operation"] == "update"
    assert events[0]["afterHash"] == hashlib.sha256(b"new").hexdigest()


def test_edit_projects_file_changed(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "b.py"
    target.write_text("old", encoding="utf-8")
    projector = ToolProjector(str(workspace))
    projector.on_tool_call(
        tool_call("s1", "edit", "c1", {"file_path": "b.py", "old_string": "old", "new_string": "new"})
    )
    target.write_text("new", encoding="utf-8")

    events = projector.on_tool_result(tool_result("s1", "c1"), task_id="t1")

    assert events[0]["operation"] == "update"


def test_bash_pytest_projects_test_result(tmp_path):
    projector = ToolProjector(str(tmp_path))
    projector.on_tool_call(
        tool_call(
            "s1",
            "bash",
            "c1",
            {"command": "python -m pytest tests/test_x.py -q"},
        )
    )

    events = projector.on_tool_result(
        tool_result("s1", "c1", text="=== 3 passed, 1 failed in 1.23s ==="),
        task_id="t1",
    )

    test_event = next(e for e in events if e["type"] == "agent.task.test_result")
    assert test_event["command"] == "python -m pytest tests/test_x.py -q"
    assert test_event["passed"] == 3
    assert test_event["failed"] == 1
    assert test_event["durationMs"] == 1230


def test_non_test_bash_projects_nothing(tmp_path):
    projector = ToolProjector(str(tmp_path))
    projector.on_tool_call(
        tool_call("s1", "bash", "c1", {"command": "python runtime/server.py --check"})
    )

    assert projector.on_tool_result(tool_result("s1", "c1"), task_id="t1") == []


def test_failed_tool_result_projects_nothing(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    projector = ToolProjector(str(workspace))
    projector.on_tool_call(
        tool_call("s1", "write", "c1", {"file_path": "x.txt", "content": "x"})
    )
    notification = tool_result("s1", "c1")
    notification["event"]["data"]["error"] = {"name": "ToolError"}

    assert projector.on_tool_result(notification, task_id="t1") == []


def test_real_wire_shape_write_result(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "new.txt"
    projector = ToolProjector(str(workspace))
    projector.on_tool_call(
        tool_call("s1", "write", "c1", {"file_path": "new.txt", "content": "hi"})
    )
    target.write_text("hi", encoding="utf-8")
    notification = {
        "sessionId": "s1",
        "event": {
            "type": "tool/result",
            "data": {
                "message": {
                    "source": {"kind": "tool", "callId": "c1"},
                    "content": [
                        {
                            "type": "tool-result",
                            "toolCallId": "c1",
                            "content": [{"type": "text", "text": "ok"}],
                        }
                    ],
                }
            },
        },
    }

    events = projector.on_tool_result(notification, task_id="t1")

    assert len(events) == 1
    assert events[0]["type"] == "agent.task.file_changed"
    assert events[0]["operation"] == "create"


def test_real_wire_shape_pytest_result(tmp_path):
    projector = ToolProjector(str(tmp_path))
    projector.on_tool_call(
        tool_call(
            "s1",
            "bash",
            "c1",
            {"command": "python -m pytest tests/test_runtime_checks.py -q; echo EXIT_CODE=$?"},
        )
    )
    notification = {
        "sessionId": "s1",
        "event": {
            "type": "tool/result",
            "data": {
                "message": {
                    "source": {"kind": "tool", "callId": "c1"},
                    "content": [
                        {
                            "type": "tool-result",
                            "toolCallId": "c1",
                            "content": [
                                {"type": "text", "text": "....\n4 passed in 0.39s\nEXIT_CODE=0"}
                            ],
                        }
                    ],
                }
            },
        },
    }

    events = projector.on_tool_result(notification, task_id="t1")

    test_event = next(e for e in events if e["type"] == "agent.task.test_result")
    assert test_event["passed"] == 4
    assert test_event["failed"] == 0
