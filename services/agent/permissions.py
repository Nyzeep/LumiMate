"""权限策略：§13 Low/Medium/High 分级、Medium 四元组 Grant、无自动提升路径。"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, FrozenSet, Mapping

from services.agent.command_policy import classify_bash_command
from services.agent.models import Grant


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


LOW_ACTIONS: FrozenSet[str] = frozenset(
    {"read", "read_image", "search", "grep", "git_status", "plan", "todo", "list"}
)

MEDIUM_ACTIONS: FrozenSet[str] = frozenset(
    {"write", "edit", "str_replace_editor", "test", "pytest", "lint", "typecheck"}
)

HIGH_ACTIONS: FrozenSet[str] = frozenset(
    {
        "delete",
        "remove",
        "dependency_modify",
        "config_modify",
        "install",
        "network",
        "system_program",
        "system_settings",
    }
)

MEDIUM_CATEGORIES: FrozenSet[str] = frozenset(
    {"file_modify", "test", "lint", "typecheck"}
)

CATEGORY_FOR_ACTION: Mapping[str, str] = {
    "write": "file_modify",
    "edit": "file_modify",
    "str_replace_editor": "file_modify",
    "test": "test",
    "pytest": "test",
    "lint": "lint",
    "typecheck": "typecheck",
}

HIGH_RISK_COMMAND_KEYWORDS: tuple[str, ...] = (
    "install",
    "pip ",
    "rm ",
    "del ",
    "remove-",
    "curl ",
    "wget ",
    "http://",
    "https://",
    "start ",
    "taskkill",
)


def _is_inside(path_value: str, workspace: str) -> bool:
    try:
        path = Path(path_value)
        root = Path(workspace)
        if not path.is_absolute():
            path = root / path
        resolved = path.resolve()
        resolved_root = root.resolve()
    except OSError:
        return False
    return resolved.is_relative_to(resolved_root)

def classify_action(
    action: str,
    *,
    path: str | None = None,
    workspace: str | None = None,
    command: str | None = None,
) -> RiskLevel:
    """§13 分级：读/计划类 Low；文件修改/测试类 Medium；删除/安装/网络等 High。"""
    name = (action or "").strip().lower()
    if path and (not workspace or not _is_inside(path, workspace)):
        return RiskLevel.HIGH
    if name in HIGH_ACTIONS:
        return RiskLevel.HIGH
    if name in MEDIUM_ACTIONS:
        return RiskLevel.MEDIUM
    if name in LOW_ACTIONS:
        return RiskLevel.LOW
    if name == "bash":
        cmd = (command or "").strip().lower()
        for keyword in HIGH_RISK_COMMAND_KEYWORDS:
            if keyword in cmd:
                return RiskLevel.HIGH
        command_kind = classify_bash_command(cmd)
        if command_kind == "check":
            return RiskLevel.MEDIUM
        if command_kind == "git":
            return RiskLevel.LOW
        return RiskLevel.HIGH
    return RiskLevel.HIGH


def category_for_action(action: str, *, command: str | None = None) -> str:
    """Return the Grant category represented by an authorized action."""
    name = (action or "").strip().lower()
    if name == "bash":
        command_kind = classify_bash_command(command)
        if command_kind == "check":
            return "test"
        if command_kind == "git":
            return "git_status"
        return "command"
    return CATEGORY_FOR_ACTION.get(name, name)


class PermissionPolicy:
    """Grant 四元组管理：taskId + sessionId + workspace + category。"""

    def __init__(self) -> None:
        self._grants: dict[tuple[str, str, str, str], Grant] = {}

    def grant(
        self,
        *,
        task_id: str,
        session_id: str,
        workspace: str,
        category: str,
    ) -> Grant:
        if category not in MEDIUM_CATEGORIES:
            raise ValueError(f"只有 Medium 类别可以 Grant：{category}")
        grant = Grant(
            task_id=task_id,
            session_id=session_id,
            workspace=workspace,
            category=category,
        )
        self._grants[(task_id, session_id, workspace, category)] = grant
        return grant

    def check(
        self,
        *,
        task_id: str,
        session_id: str,
        workspace: str,
        action: str,
        path: str | None = None,
        command: str | None = None,
    ) -> tuple[RiskLevel, str]:
        """返回 (风险等级, "allow" | "ask")；High 恒 ask，Medium 需有效 Grant。"""
        level = classify_action(action, path=path, workspace=workspace, command=command)
        if level is RiskLevel.LOW:
            return level, "allow"
        if level is RiskLevel.HIGH:
            return level, "ask"
        category = category_for_action(action, command=command)
        key = (task_id, session_id, workspace, category)
        if key in self._grants:
            return level, "allow"
        return level, "ask"

    def revoke_for_task(self, task_id: str) -> None:
        stale = [key for key in self._grants if key[0] == task_id]
        for key in stale:
            self._grants.pop(key, None)

    def revoke_for_workspace(self, workspace: str) -> None:
        stale = [key for key in self._grants if key[2] != workspace]
        for key in stale:
            self._grants.pop(key, None)
