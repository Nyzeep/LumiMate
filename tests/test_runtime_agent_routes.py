from fastapi.testclient import TestClient

from runtime.server import create_app


def test_agent_status_endpoint_shape():
    app = create_app()
    with TestClient(app) as client:
        response = client.post("/api/agent/status")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["ready"] is True
    assert body["harnessAvailable"] is False
    assert body["currentTask"] is None
    assert body["sessions"] == []


from pathlib import Path

from fastapi.testclient import TestClient

from runtime.server import create_app
from services.agent.service import AgentService
from services.agent.store import TaskStore
from tests.test_agent_service import FakeBridge

WORKSPACE = r"D:\LumiMate"


def make_http_service(tmp_path: Path, with_stores: bool = False):
    from services.agent.memory import MemoryStore
    from services.agent.persistence import ProjectionStore

    bridge = FakeBridge()
    service = AgentService(
        store=TaskStore(tmp_path / "tasks"),
        sessions_root=tmp_path / "sessions",
        bridge=bridge,
        publisher=lambda _event: None,
        workspace=WORKSPACE,
        projections=ProjectionStore(tmp_path / "projections") if with_stores else None,
        memory=MemoryStore(tmp_path / "memory") if with_stores else None,
    )
    return service, bridge

def test_agent_status_with_service_returns_service_status(tmp_path):
    service, _ = make_http_service(tmp_path)
    app = create_app(agent_service=service)
    with TestClient(app) as client:
        response = client.post("/api/agent/status")
    body = response.json()
    assert body["ok"] is True
    assert body["harnessAvailable"] is True
    assert body["currentTask"] is None
    assert body["sessions"] == []


def test_task_start_and_cancel_via_http(tmp_path):
    service, bridge = make_http_service(tmp_path)
    app = create_app(agent_service=service)
    with TestClient(app) as client:
        start_response = client.post(
            "/api/agent/task/start",
            json={"title": "修复测试", "goal": "让 pytest 全绿", "workspace": WORKSPACE},
        )
    start_body = start_response.json()
    assert start_body["ok"] is True
    task = start_body["task"]
    assert task["state"] == "planning"
    assert bridge.runs[-1][1] == task["taskId"]

    with TestClient(app) as client:
        cancel_response = client.post(
            "/api/agent/task/cancel", json={"taskId": task["taskId"]}
        )
    assert cancel_response.json()["task"]["state"] == "cancelled"


def test_task_start_rejects_foreign_workspace_via_http(tmp_path):
    service, _ = make_http_service(tmp_path)
    app = create_app(agent_service=service)
    with TestClient(app) as client:
        response = client.post(
            "/api/agent/task/start",
            json={"title": "越权", "goal": "x", "workspace": r"C:\Other"},
        )
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "INVALID_WORKSPACE"


def test_agent_not_configured_defaults(tmp_path):
    app = create_app()
    with TestClient(app) as client:
        status = client.post("/api/agent/status")
        start = client.post(
            "/api/agent/task/start",
            json={"title": "t", "goal": "g", "workspace": WORKSPACE},
        )
    assert status.json()["harnessAvailable"] is False
    assert start.json()["ok"] is False
    assert start.json()["error"]["code"] == "AGENT_NOT_CONFIGURED"


def test_session_resume_and_list_via_http(tmp_path):
    service, bridge = make_http_service(tmp_path)
    app = create_app(agent_service=service)
    with TestClient(app) as client:
        resume = client.post(
            "/api/agent/session/resume",
            json={
                "sessionId": "s-existing",
                "title": "续跑",
                "goal": "继续",
                "workspace": WORKSPACE,
            },
        )
        listing = client.post("/api/agent/session/list")
    resume_body = resume.json()
    assert resume_body["ok"] is True
    assert resume_body["task"]["sessionId"] == "s-existing"
    assert bridge.runs[-1][0] == "s-existing"
    assert any(s["sessionId"] == "s-existing" for s in listing.json()["sessions"])




def test_permission_approval_flow_via_http(tmp_path):
    service, bridge = make_http_service(tmp_path)
    app = create_app(agent_service=service)
    with TestClient(app) as client:
        start_response = client.post(
            "/api/agent/task/start",
            json={"title": "t", "goal": "g", "workspace": WORKSPACE},
        )
    task = start_response.json()["task"]
    task_id = task["taskId"]
    session_id = task["sessionId"]
    bridge.last_results[session_id] = type(
        "Result", (), {"final_response": "计划"}
    )()
    service.on_bridge_event(
        {
            "type": "agent.task.completed",
            "taskId": task_id,
            "sessionId": session_id,
        }
    )
    with TestClient(app) as client:
        approve_plan = client.post(
            "/api/agent/task/approve",
            json={"taskId": task_id, "kind": "plan", "approve": True},
        )
        assert approve_plan.json()["task"]["state"] == "running"

    service.on_bridge_tool_call(
        {
            "sessionId": session_id,
            "event": {
                "type": "tool/call",
                "data": {
                    "name": "write",
                    "callId": "call-1",
                    "arguments": '{"file_path": "D:\\\\LumiMate\\\\a.py"}',
                },
            },
        },
        task_id=task_id,
    )
    assert service.get_task(task_id).state.value == "awaiting_permission"

    with TestClient(app) as client:
        permission = client.post(
            "/api/agent/task/approve",
            json={
                "taskId": task_id,
                "kind": "permission",
                "requestId": "call-1",
                "grantCategory": "file_modify",
                "approve": True,
            },
        )
    assert permission.json()["task"]["state"] == "running"
    assert bridge.approval_answers == [(session_id, "call-1", True)]


def test_memory_propose_and_confirm_via_http(tmp_path):
    service, _ = make_http_service(tmp_path, with_stores=True)
    app = create_app(agent_service=service)
    with TestClient(app) as client:
        propose = client.post(
            "/api/agent/memory/propose",
            json={"summary": "用户偏好 pytest", "kind": "preference", "sourceTaskId": "t1"},
        )
    propose_body = propose.json()
    assert propose_body["ok"] is True
    proposal_id = propose_body["proposal"]["proposalId"]
    assert propose_body["proposal"]["status"] == "pending"

    with TestClient(app) as client:
        confirm = client.post(
            "/api/agent/memory/confirm",
            json={"proposalId": proposal_id, "accept": True},
        )
    assert confirm.json()["proposal"]["status"] == "accepted"
    assert len(service._memory.list_memories()) == 1


def test_memory_confirm_unknown_proposal_via_http(tmp_path):
    service, _ = make_http_service(tmp_path, with_stores=True)
    app = create_app(agent_service=service)
    with TestClient(app) as client:
        response = client.post(
            "/api/agent/memory/confirm",
            json={"proposalId": "memory-nope", "accept": True},
        )
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "MEMORY_INVALID"
