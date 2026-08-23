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


def make_http_service(tmp_path: Path):
    bridge = FakeBridge()
    service = AgentService(
        store=TaskStore(tmp_path / "tasks"),
        sessions_root=tmp_path / "sessions",
        bridge=bridge,
        publisher=lambda _event: None,
        workspace=WORKSPACE,
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


