import json

from services.agent.permissions import PermissionPolicy, RiskLevel
from services.agent.tools.authorization import (
    PUBLIC_ARGUMENTS_REDACTION,
    ToolAuthorizationGate,
)


WORKSPACE = r"D:\LumiMate"


def test_wire_call_keeps_raw_facts_private_from_public_projection():
    gate = ToolAuthorizationGate(PermissionPolicy())
    wire = {
        "sessionId": "s1",
        "event": {
            "type": "tool/call",
            "data": {
                "callId": "c1",
                "name": "write",
                "arguments": json.dumps(
                    {"file_path": "services/a.py", "content": "private"}
                ),
            },
        },
    }

    call = gate.from_wire(wire, task_id="t1")
    assert call is not None
    assert call.arguments["file_path"] == "services/a.py"

    public_event = gate.project_started(call)
    assert public_event["arguments"] == PUBLIC_ARGUMENTS_REDACTION
    assert "services/a.py" not in str(public_event)
    assert "private" not in str(public_event)


def _wire(tool_name, call_id, arguments, session_id="s1"):
    return {
        "sessionId": session_id,
        "event": {
            "type": "tool/call",
            "data": {"name": tool_name, "callId": call_id, "arguments": arguments},
        },
    }


def test_gate_uses_raw_command_for_whitelist_and_medium_category():
    gate = ToolAuthorizationGate(PermissionPolicy())
    call = gate.from_wire(
        _wire("bash", "c1", json.dumps({"command": "python -m pytest tests -q"})),
        task_id="t1",
    )

    decision = gate.decide(call, workspace=WORKSPACE)
    assert decision.level == RiskLevel.MEDIUM
    assert decision.kind == "ask"
    assert decision.category == "test"


def test_gate_keeps_workspace_escape_at_high_risk():
    gate = ToolAuthorizationGate(PermissionPolicy())
    call = gate.from_wire(
        _wire("write", "c1", json.dumps({"file_path": "../outside.py"})),
        task_id="t1",
    )

    decision = gate.decide(call, workspace=WORKSPACE)
    assert decision.level == RiskLevel.HIGH
    assert decision.kind == "ask"


def test_unparseable_arguments_fail_closed():
    gate = ToolAuthorizationGate(PermissionPolicy())
    call = gate.from_wire(
        _wire("bash", "c1", "not-json{{{"),
        task_id="t1",
    )

    decision = gate.decide(call, workspace=WORKSPACE)
    assert decision.kind == "reject"


def test_missing_call_id_fails_closed():
    gate = ToolAuthorizationGate(PermissionPolicy())
    call = gate.from_wire(
        _wire("write", "", json.dumps({"file_path": "a.py"})),
        task_id="t1",
    )

    decision = gate.decide(call, workspace=WORKSPACE)
    assert decision.kind == "reject"


def test_session_mismatch_fails_closed():
    gate = ToolAuthorizationGate(PermissionPolicy())
    call = gate.from_wire(
        _wire("write", "c1", json.dumps({"file_path": "a.py"})),
        task_id="t1",
    )

    decision = gate.decide(
        call,
        workspace=WORKSPACE,
        expected_session_id="s2",
    )
    assert decision.kind == "reject"
