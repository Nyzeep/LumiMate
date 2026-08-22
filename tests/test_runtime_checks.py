from fastapi.testclient import TestClient

from runtime.server import (
    _format_bytes,
    _normalize_ambient_mode,
    _normalize_scene,
    create_app,
)


def test_normalize_scene_keeps_valid_scene_and_falls_back_to_home():
    assert _normalize_scene("chat") == "chat"
    assert _normalize_scene("nope") == "home"
    assert _normalize_scene("") == "home"


def test_normalize_ambient_mode_keeps_valid_mode_and_falls_back_to_quiet():
    assert _normalize_ambient_mode("breath") == "breath"
    assert _normalize_ambient_mode("loud") == "quiet"


def test_format_bytes():
    assert _format_bytes(0) == "0 B"
    assert _format_bytes(1024) == "1.00 KB"
    assert _format_bytes(1536) == "1.50 KB"
    assert _format_bytes(1024**3) == "1.00 GB"


def test_health_endpoint():
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True, "version": "0.2.0"}
