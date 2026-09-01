"""Harness wire events to proposal section 8 Agent events and TaskState."""

from __future__ import annotations

import re
from typing import Any

from services.agent.events import build_agent_event


def _safe_status(value: Any) -> int | None:
    try:
        status = int(value)
    except (TypeError, ValueError):
        return None
    return status if 100 <= status <= 599 else None


def _diagnostic_message(reason: str, status: int | None) -> str:
    """Build a useful Task diagnosis from allowlisted, non-secret facts only."""
    if reason == "AUTH":
        return f"Authentication failed (HTTP {status})" if status else "Authentication failed"
    if status is not None:
        return f"Harness request failed (HTTP {status})"
    return ""


def _failure_payload(value: Any, *, fallback_reason: str = "error") -> dict[str, Any]:
    """Project only structured, non-secret Harness failure facts to a Task."""
    source = value
    if isinstance(value, dict) and isinstance(value.get("error"), dict):
        source = value["error"]

    raw_code: Any = None
    raw_status: Any = None
    raw_message: Any = value if not isinstance(value, dict) else ""
    if isinstance(source, dict):
        raw_code = source.get("code")
        raw_status = source.get("status")
        raw_message = source.get("message") or ""

    message_for_classification = str(raw_message or "")
    provider_code = str(raw_code or "").strip()
    is_auth = provider_code == "AUTH" or re.search(
        r"\bauth(?:entication)?\b|api[_ ]?key",
        message_for_classification,
        re.IGNORECASE,
    )

    status = _safe_status(raw_status)
    if status is None:
        status_match = re.search(r"\b([45]\d{2})\b", message_for_classification)
        status = _safe_status(status_match.group(1)) if status_match else None

    reason = "AUTH" if is_auth else fallback_reason
    if not is_auth and status is not None and 400 <= status <= 599:
        reason = f"HTTP_{status // 100}XX"
    failure: dict[str, Any] = {"reason": reason}
    if status is not None:
        failure["status"] = status
    diagnostic = _diagnostic_message(reason, status)
    if diagnostic:
        failure["message"] = diagnostic
    return failure


def failure_from_turn_reason(reason: Any) -> dict[str, Any]:
    """Map a public Harness turn-end reason to a redacted Task failure."""
    return _failure_payload(reason)


def failure_from_exception(exc: Exception) -> dict[str, Any]:
    """Map an SDK transport exception without leaking its credentials."""
    return _failure_payload(str(exc))


def _failure_from_run_result(result: Any) -> dict[str, Any]:
    events = getattr(result, "events", None)
    if isinstance(events, list):
        for event in reversed(events):
            if not isinstance(event, dict) or event.get("type") != "turn/end":
                continue
            data = event.get("data")
            reason = data.get("reason") if isinstance(data, dict) else None
            if isinstance(reason, dict) and reason.get("kind") == "error":
                return failure_from_turn_reason(reason)
    return {"reason": "error"}


def map_session_status(
    session_id: str,
    status: str,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Map a session.status notification to agent.session.updated."""
    return build_agent_event(
        "agent.session.updated",
        task_id=task_id,
        session_id=session_id,
        status=status,
        summary="",
    )


def map_session_event(
    notification: dict[str, Any],
    task_id: str | None = None,
) -> list[dict[str, Any]]:
    """Map one session.event notification to zero or more Agent events."""
    if not isinstance(notification, dict):
        return []
    session_id = str(notification.get("sessionId") or "")
    event = notification.get("event")
    if not isinstance(event, dict):
        return []
    data = event.get("data")
    if not isinstance(data, dict):
        return []
    event_type = str(event.get("type") or "")

    if event_type == "tool/call":
        return [
            build_agent_event(
                "agent.task.tool_started",
                task_id=task_id,
                session_id=session_id,
                toolName=str(data.get("name") or "unknown"),
                callId=str(data.get("callId") or ""),
                status="running",
                arguments=(
                    "arguments omitted for privacy"
                    if data.get("arguments") not in (None, "")
                    else ""
                ),
            )
        ]

    if event_type == "tool/result":
        return [
            build_agent_event(
                "agent.task.tool_finished",
                task_id=task_id,
                session_id=session_id,
                toolName=str(data.get("name") or "unknown"),
                callId=str(data.get("callId") or ""),
                status="error" if data.get("error") else "ok",
            )
        ]

    if event_type == "turn/end":
        turn_reason = data.get("reason")
        reason = turn_reason.get("kind") if isinstance(turn_reason, dict) else ""
        if reason == "completed":
            return [
                build_agent_event(
                    "agent.task.completed",
                    task_id=task_id,
                    session_id=session_id,
                )
            ]
        if reason == "error":
            return [
                build_agent_event(
                    "agent.task.failed",
                    task_id=task_id,
                    session_id=session_id,
                    failure=failure_from_turn_reason(turn_reason),
                )
            ]

    return []


def map_subagent_notification(
    notification: dict[str, Any],
    task_id: str | None = None,
) -> list[dict[str, Any]]:
    """Subagent notifications are projection-only and emit no section 8 event."""
    return []


def map_run_result(
    result: Any,
    task_id: str | None = None,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """Map RunResult.finish_reason to a terminal Task event."""
    reason = getattr(result, "finish_reason", None)
    if reason == "completed":
        return [
            build_agent_event(
                "agent.task.completed",
                task_id=task_id,
                session_id=session_id,
            )
        ]
    return [
        build_agent_event(
            "agent.task.failed",
            task_id=task_id,
            session_id=session_id,
            failure=_failure_from_run_result(result),
        )
    ]
