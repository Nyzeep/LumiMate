"""Harness wire 事件 → 提案 §8 Agent 事件 / TaskState 的纯映射。"""

from __future__ import annotations

from typing import Any

from services.agent.events import build_agent_event


def map_session_status(
    session_id: str,
    status: str,
    task_id: str | None = None,
) -> dict[str, Any]:
    """`session.status` 通知 → `agent.session.updated` 事件。"""
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
    """`session.event` 通知 → 0..n 个 §8 Agent 事件。"""
    session_id = str(notification.get("sessionId") or "")
    event = notification.get("event") or {}
    event_type = str(event.get("type") or "")
    data = event.get("data") or {}

    if event_type == "tool/call":
        return [
            build_agent_event(
                "agent.task.tool_started",
                task_id=task_id,
                session_id=session_id,
                toolName=str(data.get("name") or "unknown"),
                callId=str(data.get("callId") or ""),
                status="running",
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
        reason = (data.get("reason") or {}).get("kind")
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
                    failure={"reason": "error"},
                )
            ]

    return []


def map_subagent_notification(
    notification: dict[str, Any],
    task_id: str | None = None,
) -> list[dict[str, Any]]:
    """`subagent.started` / `subagent.finished` 通知：仅用于投影，不产生 §8 事件。"""
    return []


def map_run_result(
    result: Any,
    task_id: str | None = None,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """`RunResult.finish_reason` → 终态事件（completed / failed）。"""
    reason = getattr(result, "finish_reason", None)
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
                failure={"reason": "error"},
            )
        ]
    return []

