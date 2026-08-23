"""工具/命令白名单：提案 §13 工具集与 §20 测试命令白名单。"""

from __future__ import annotations

from typing import Any, FrozenSet, Mapping

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

ALLOWED_CHECK_COMMANDS: tuple[str, ...] = (
    "pytest",
    "npm run build",
    "runtime/server.py --check",
)

ALLOWED_GIT_COMMANDS: tuple[str, ...] = (
    "git status",
    "git diff",
    "git log",
    "git rev-parse",
    "git branch",
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
    if any(marker in command for marker in ALLOWED_CHECK_COMMANDS):
        return True
    return any(command.startswith(git) for git in ALLOWED_GIT_COMMANDS)
