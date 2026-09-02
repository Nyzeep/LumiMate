import os
import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from runtime.server import create_app
from services.agent.runtime import build_agent_service, build_harness_client, load_api_key
from services.agent.service import AgentService


def _install_fake_harness(monkeypatch, harness_class) -> list[str]:
    runtime_modes: list[str] = []

    def resolve_bundled_launch_args(mode: str) -> list[str]:
        runtime_modes.append(mode)
        return ["node", "fake-runtime"]

    monkeypatch.setitem(
        sys.modules,
        "deepseek_harness",
        SimpleNamespace(DeepSeekHarness=harness_class),
    )
    monkeypatch.setitem(
        sys.modules,
        "deepseek_harness_runtime",
        SimpleNamespace(resolve_bundled_launch_args=resolve_bundled_launch_args),
    )
    return runtime_modes


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


def test_build_harness_client_uses_the_public_sdk_configuration(tmp_path, monkeypatch):
    endpoint = "https://gateway.example/v1"
    (tmp_path / ".env").write_text(
        "DEEPSEEK_API_KEY=sk-test-key\nDEEPSEEK_BASE_URL=https://gateway.example/v1\n",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    class FakeHarness:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    runtime_modes = _install_fake_harness(monkeypatch, FakeHarness)

    client = build_harness_client(tmp_path)

    assert isinstance(client, FakeHarness)
    assert captured["base_url"] == endpoint
    assert captured["cwd"] == str(tmp_path)
    assert captured["launch_args_override"]
    assert runtime_modes == ["node"]


def test_build_harness_client_keeps_dsh_configuration_local_to_sdk(tmp_path, monkeypatch):
    names = (
        "DSH_RUNTIME_MODE",
        "DSH_CWD",
        "DSH_SESSION_ROOT",
        "DSH_CORDIS_CONFIG",
        "DSH_APPROVAL_INBOX",
        "DSH_APPROVAL_OUTBOX",
    )
    for name in names:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / ".env").write_text("DEEPSEEK_API_KEY=sk-test-key\n", encoding="utf-8")
    captured: dict[str, object] = {}

    class FakeHarness:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    _install_fake_harness(monkeypatch, FakeHarness)

    build_harness_client(tmp_path)

    assert all(name not in os.environ for name in names)
    assert "DSH_RUNTIME_MODE" not in captured["env"]
    assert captured["env"]["DSH_APPROVAL_INBOX"] == str(tmp_path / ".agent" / "approval-inbox")


def test_task_agent_passes_env_file_endpoint_to_harness(tmp_path, monkeypatch):
    endpoint = "https://gateway.example/v1"
    (tmp_path / ".env").write_text(
        "DEEPSEEK_API_KEY=sk-test-key\nDEEPSEEK_BASE_URL=https://gateway.example/v1\n",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    class FakeHarness:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def start(self) -> None:
            pass

        def run(self, *_args, **_kwargs):
            return SimpleNamespace(finish_reason="error", final_response="", events=[])

        def close(self) -> None:
            pass

    _install_fake_harness(monkeypatch, FakeHarness)
    service = build_agent_service(tmp_path, lambda _event: None)
    task = service.start_task("endpoint check", "read only", str(tmp_path))

    assert service._bridge.wait_for_turn(task.session_id, timeout=2) is True
    assert captured["base_url"] == endpoint
    service.close()
