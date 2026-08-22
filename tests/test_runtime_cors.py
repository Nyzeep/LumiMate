from fastapi.testclient import TestClient

from runtime.server import create_app

ALLOWED_ORIGIN = "http://127.0.0.1:5173"
DISALLOWED_ORIGIN = "http://evil.example"


def _preflight(client, origin):
    return client.options(
        "/api/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )


def test_allowed_dev_origin_gets_cors_header():
    app = create_app()
    with TestClient(app) as client:
        response = _preflight(client, ALLOWED_ORIGIN)
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN


def test_disallowed_origin_gets_no_cors_header():
    app = create_app()
    with TestClient(app) as client:
        response = _preflight(client, DISALLOWED_ORIGIN)
    assert "access-control-allow-origin" not in response.headers


def test_cors_origins_env_override(monkeypatch):
    custom = "http://lan.lumimate.local:8080"
    monkeypatch.setenv("LUMIMATE_CORS_ORIGINS", custom)
    app = create_app()
    with TestClient(app) as client:
        response = _preflight(client, custom)
    assert response.headers.get("access-control-allow-origin") == custom
