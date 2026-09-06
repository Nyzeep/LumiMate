"""Private tool authorization seam and safe public event projections."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal, Mapping

from services.agent.events import build_agent_event
from services.agent.permissions import (
    PermissionPolicy,
    RiskLevel,
    category_for_action,
)
from services.agent.tools.registry import is_allowed_tool

PUBLIC_ARGUMENTS_REDACTION = "arguments omitted for privacy"
DecisionKind = Literal["allow", "ask", "reject"]


@dataclass(frozen=True)
class ToolCall:
    """Raw tool facts retained behind the Bridge-to-Agent seam."""

    task_id: str
    session_id: str
    tool_name: str
    call_id: str
    arguments: dict[str, Any]
    has_arguments: bool
    arguments_valid: bool


@dataclass(frozen=True)
class ToolDecision:
    kind: DecisionKind
    level: RiskLevel | None
    category: str
    reason: str = ""


@dataclass(frozen=True)
class PendingTool:
    call: ToolCall
    decision: ToolDecision


class ToolAuthorizationGate:
    """Keep raw tool facts private while centralizing whitelist and risk decisions."""

    def __init__(self, policy: PermissionPolicy) -> None:
        self._policy = policy

    def from_wire(
        self,
        notification: Mapping[str, Any],
        *,
        task_id: str,
    ) -> ToolCall | None:
        if not isinstance(notification, Mapping):
            return None
        event = notification.get("event")
        if not isinstance(event, Mapping) or event.get("type") != "tool/call":
            return None
        data = event.get("data")
        if not isinstance(data, Mapping):
            return None
        return self._from_parts(
            task_id=task_id,
            session_id=str(notification.get("sessionId") or ""),
            tool_name=data.get("name"),
            call_id=data.get("callId"),
            raw_arguments=data.get("arguments"),
        )

    def decide(
        self,
        call: ToolCall,
        *,
        workspace: str,
        expected_session_id: str | None = None,
    ) -> ToolDecision:
        category = category_for_action(
            call.tool_name,
            command=str(call.arguments.get("command") or "") or None,
        )
        if not call.call_id:
            return ToolDecision(
                kind="reject",
                level=RiskLevel.HIGH,
                category=category,
                reason="工具调用缺少 callId",
            )
        if expected_session_id is not None and call.session_id != expected_session_id:
            return ToolDecision(
                kind="reject",
                level=RiskLevel.HIGH,
                category=category,
                reason="工具调用 Session 与 Task 不匹配",
            )
        if not call.arguments_valid:
            return ToolDecision(
                kind="reject",
                level=RiskLevel.HIGH,
                category=category,
                reason="工具参数无效",
            )
        if not is_allowed_tool(call.tool_name, call.arguments):
            return ToolDecision(
                kind="reject",
                level=RiskLevel.HIGH,
                category=category,
                reason="工具不在白名单内",
            )

        path = call.arguments.get("file_path") or call.arguments.get("path")
        command = call.arguments.get("command")
        level, decision = self._policy.check(
            task_id=call.task_id,
            session_id=call.session_id,
            workspace=workspace,
            action=call.tool_name,
            path=str(path) if path else None,
            command=str(command) if command else None,
        )
        return ToolDecision(
            kind="allow" if decision == "allow" else "ask",
            level=level,
            category=category,
        )

    @staticmethod
    def project_started(call: ToolCall) -> dict[str, Any]:
        return build_agent_event(
            "agent.task.tool_started",
            task_id=call.task_id,
            session_id=call.session_id,
            toolName=call.tool_name,
            callId=call.call_id,
            status="running",
            arguments=PUBLIC_ARGUMENTS_REDACTION if call.has_arguments else "",
        )

    @staticmethod
    def project_permission(
        call: ToolCall,
        decision: ToolDecision,
    ) -> dict[str, Any]:
        return build_agent_event(
            "agent.task.awaiting_permission",
            task_id=call.task_id,
            session_id=call.session_id,
            requestId=call.call_id,
            category=decision.category,
            toolName=call.tool_name,
            details={"argumentKeys": sorted(str(key) for key in call.arguments)},
        )

    @staticmethod
    def project_rejected(
        call: ToolCall,
        decision: ToolDecision,
    ) -> dict[str, Any]:
        return build_agent_event(
            "agent.task.tool_finished",
            task_id=call.task_id,
            session_id=call.session_id,
            toolName=call.tool_name,
            callId=call.call_id,
            status="error",
            summary=decision.reason,
        )

    @staticmethod
    def _from_parts(
        *,
        task_id: str,
        session_id: str,
        tool_name: Any,
        call_id: Any,
        raw_arguments: Any,
    ) -> ToolCall:
        arguments, has_arguments, arguments_valid = _parse_arguments(raw_arguments)
        return ToolCall(
            task_id=str(task_id or ""),
            session_id=session_id,
            tool_name=str(tool_name or "").strip().lower(),
            call_id=str(call_id or ""),
            arguments=arguments,
            has_arguments=has_arguments,
            arguments_valid=arguments_valid,
        )


def _parse_arguments(raw: Any) -> tuple[dict[str, Any], bool, bool]:
    """Return parsed arguments, whether they were supplied, and whether they are valid."""
    if raw is None or raw == "":
        return {}, False, True
    if isinstance(raw, Mapping):
        return dict(raw), True, True
    if not isinstance(raw, str) or not raw.strip():
        return {}, True, False
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return {}, True, False
    if not isinstance(parsed, dict):
        return {}, True, False
    return parsed, True, True
