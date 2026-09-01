"""Agent 运行时真实装配：把 AgentService 接上 Harness SDK、落盘与 WebSocket 发布。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from services.agent.bridge.harness_bridge import HarnessBridge
from services.agent.memory import MemoryStore
from services.agent.persistence import ProjectionStore
from services.agent.service import AgentService
from services.agent.store import TaskStore
from services.agent.tools.normalizer import ToolProjector

DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_PROVIDER = "deepseek-official"


def load_environment_value(workspace: str | Path, env_name: str) -> str:
    """从环境变量或 gitignored 的 .env 读取一个 Harness 配置值。"""
    from_env = os.environ.get(env_name, "").strip()
    if from_env:
        return from_env
    env_file = Path(workspace) / ".env"
    if env_file.exists():
        for raw in env_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith(f"{env_name}="):
                return line.split("=", 1)[1].strip()
    return ""


def load_api_key(workspace: str | Path, env_name: str = "DEEPSEEK_API_KEY") -> str:
    """读取 Key；不落库、不进 Git。"""
    return load_environment_value(workspace, env_name)


def build_harness_client(
    workspace: str | Path,
    *,
    cordis_config: str | Path | None = None,
) -> Any:
    """Construct the public Harness SDK client used by Task Agent and diagnostics."""
    from deepseek_harness import DeepSeekHarness
    from deepseek_harness_runtime import resolve_bundled_launch_args

    root = Path(workspace)
    agent_dir = root / ".agent"
    approval_inbox = agent_dir / "approval-inbox"
    approval_outbox = agent_dir / "approval-outbox"
    sessions_root = agent_dir / "sessions"
    default_cordis = root / ".scratch" / "agent-upgrade" / "spike" / "cordis.yml"
    cordis = Path(cordis_config) if cordis_config else default_cordis
    api_key = load_api_key(root)
    base_url = load_environment_value(root, "DEEPSEEK_BASE_URL")

    return DeepSeekHarness(
        provider=DEFAULT_PROVIDER,
        model=DEFAULT_MODEL,
        api_key=api_key,
        base_url=base_url or None,
        cwd=str(root),
        session_root=str(sessions_root),
        cordis=str(cordis),
        request_timeout_seconds=240,
        shutdown_timeout_seconds=10,
        launch_args_override=resolve_bundled_launch_args("node"),
        env={
            "DSH_APPROVAL_INBOX": str(approval_inbox),
            "DSH_APPROVAL_OUTBOX": str(approval_outbox),
        },
    )


def build_agent_service(
    workspace: str | Path,
    publisher: Callable[[dict[str, Any]], None],
    *,
    cordis_config: str | Path | None = None,
) -> AgentService:
    """构造真实 AgentService；Key 惰性读取（首次启动 Harness 时才需要）。"""
    root = Path(workspace)
    agent_dir = root / ".agent"
    approval_inbox = agent_dir / "approval-inbox"
    approval_outbox = agent_dir / "approval-outbox"
    sessions_root = agent_dir / "sessions"
    default_cordis = root / ".scratch" / "agent-upgrade" / "spike" / "cordis.yml"
    cordis = Path(cordis_config) if cordis_config else default_cordis

    def client_factory() -> Any:
        return build_harness_client(root, cordis_config=cordis)

    bridge = HarnessBridge(
        client_factory,
        publisher=None,
        approval_inbox=approval_inbox,
        tool_projector=ToolProjector(root),
    )
    return AgentService(
        store=TaskStore(agent_dir / "tasks"),
        sessions_root=sessions_root,
        bridge=bridge,
        publisher=publisher,
        workspace=str(root),
        projections=ProjectionStore(agent_dir / "projections"),
        memory=MemoryStore(agent_dir / "memory"),
    )
