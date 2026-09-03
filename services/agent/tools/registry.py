"""工具/命令白名单：提案 §13 工具集与 §20 测试命令白名单。"""

from __future__ import annotations

from typing import Any, FrozenSet, Mapping

from services.agent.command_policy import (
    ALLOWED_CHECK_COMMANDS,
    ALLOWED_GIT_COMMANDS,
    classify_bash_command,
)

ALLOWED_TOOL_NAMES: FrozenSet[str] = frozenset(
    {
        "read",
        "read_image",
        "write",
        "edit",
        "bash",
        "test",
        "lint",
        "typecheck",
    }
)

def is_allowed_tool(tool_name: str, arguments: Mapping[str, Any] | None = None) -> bool:
    """白名单校验：非白名单工具/命令直接拒绝（不进入审批）。"""
    name = (tool_name or "").strip().lower()
    if name not in ALLOWED_TOOL_NAMES:
        return False
    if name != "bash":
        return True
    command = str((arguments or {}).get("command") or "").strip().lower()
    if not command:
        return False
    return classify_bash_command(command) is not None
