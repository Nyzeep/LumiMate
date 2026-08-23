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
