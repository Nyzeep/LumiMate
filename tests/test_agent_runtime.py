from pathlib import Path

from fastapi.testclient import TestClient

from runtime.server import create_app
from services.agent.runtime import build_agent_service, load_api_key
from services.agent.service import AgentService


def test_load_api_key_from_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-env-test")
    assert load_api_key("C:/tmp") == "sk-env-test"


def test_load_api_key_from_env_file(tmp_path):
    (tmp_path / ".env").write_text(
        "DEEPSEEK_API_KEY=sk-file-test\n", encoding="utf-8"
    )
    assert load_api_key(tmp_path) == "sk-file-test"


def test_build_agent_service_wires_stores_and_bridge(tmp_path):
    published: list[dict] = []

    service = build_agent_service(tmp_path, published.append)

    assert isinstance(service, AgentService)
    assert service._projections is not None
    assert service._memory is not None
    assert service._bridge._approval_inbox is not None
    assert service._bridge._tool_projector is not None
    assert service.status()["ready"] is True


def test_create_app_agent_enabled_builds_real_service(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = create_app(agent_enabled=True)

    assert app.state.agent_service is not None
    with TestClient(app) as client:
        response = client.post("/api/agent/status")
    assert response.json()["ok"] is True
    assert response.json()["harnessAvailable"] is True
