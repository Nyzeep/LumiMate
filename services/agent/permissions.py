"""权限策略：§13 Low/Medium/High 分级、Medium 四元组 Grant、无自动提升路径。"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, FrozenSet, Mapping

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

WHITELISTED_CHECK_COMMANDS: tuple[str, ...] = (
    "pytest",
    "npm run build",
    "runtime/server.py --check",
)

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
        resolved = Path(path_value).resolve()
        root = Path(workspace).resolve()
    except OSError:
        return False
    return resolved.is_relative_to(root)


def classify_action(
    action: str,
    *,
    path: str | None = None,
    workspace: str | None = None,
    command: str | None = None,
) -> RiskLevel:
    """§13 分级：读/计划类 Low；文件修改/测试类 Medium；删除/安装/网络等 High。"""
    name = (action or "").strip().lower()
    if name in HIGH_ACTIONS:
        return RiskLevel.HIGH
    if name in MEDIUM_ACTIONS:
        if path and workspace and not _is_inside(path, workspace):
            return RiskLevel.HIGH
        return RiskLevel.MEDIUM
    if name in LOW_ACTIONS:
        return RiskLevel.LOW
    if name == "bash":
        cmd = (command or "").strip().lower()
        for keyword in HIGH_RISK_COMMAND_KEYWORDS:
            if keyword in cmd:
                return RiskLevel.HIGH
        if any(marker in cmd for marker in WHITELISTED_CHECK_COMMANDS):
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH
    return RiskLevel.HIGH


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
        category = CATEGORY_FOR_ACTION.get(action, action)
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
