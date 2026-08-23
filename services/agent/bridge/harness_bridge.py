"""Harness Runtime 生命周期：后台运行、协作式取消/终止与失败回传。"""

from __future__ import annotations

import json
import re
import threading
from pathlib import Path
from typing import Any, Callable

from services.agent.bridge.wire_mapper import (
    map_run_result,
    map_session_event,
    map_session_status,
    map_subagent_notification,
)
from services.agent.events import build_agent_event


class HarnessBridge:
    """通过注入的 SDK client 驱动 Harness；同步 API 在后台线程执行，不阻塞事件循环。"""

    def __init__(
        self,
        client_factory: Callable[[], Any],
        *,
        publisher: Callable[[dict[str, Any]], None] | None = None,
        shutdown_timeout_seconds: float = 10.0,
        approval_inbox: str | Path | None = None,
    ) -> None:
        self._client_factory = client_factory
        self._publish = publisher or (lambda _event: None)
        self._shutdown_timeout = shutdown_timeout_seconds
        self._approval_inbox = Path(approval_inbox) if approval_inbox else None
        self._client: Any = None
        self._threads: dict[str, threading.Thread] = {}
        self._outcomes: dict[str, str] = {}
        self._cancel_requested: set[str] = set()
        self._lock = threading.Lock()

    def start(self) -> None:
        self._client = self._client_factory()
        self._client.start()

    def run_task(self, session_id: str, task_id: str, goal: str) -> None:
        thread = threading.Thread(
            target=self._worker,
            args=(session_id, task_id, goal),
            name=f"harness-run-{session_id}",
            daemon=True,
        )
        with self._lock:
            self._threads[session_id] = thread
        thread.start()

    def _worker(self, session_id: str, task_id: str, goal: str) -> None:
        cancelled = False
        try:
            result = self._client.run(
                goal,
                session_id=session_id,
                on_notification=lambda notification: self._on_notification(
                    notification, task_id, session_id
                ),
            )
        except Exception as exc:  # noqa: BLE001 —— SDK 传输错误统一映射为失败
            cancelled = self._is_cancel_requested(session_id)
            if cancelled:
                self._publish(
                    build_agent_event(
                        "agent.task.cancelled",
                        task_id=task_id,
                        session_id=session_id,
                    )
                )
                outcome = "cancelled"
            else:
                self._publish(
                    build_agent_event(
                        "agent.task.failed",
                        task_id=task_id,
                        session_id=session_id,
                        failure={"reason": "error"},
                    )
                )
                outcome = "failed"
        else:
            cancelled = self._is_cancel_requested(session_id)
            if cancelled:
                self._publish(
                    build_agent_event(
                        "agent.task.cancelled",
                        task_id=task_id,
                        session_id=session_id,
                    )
                )
                outcome = "cancelled"
            else:
                for event in map_run_result(
                    result,
                    task_id=task_id,
                    session_id=session_id,
                ):
                    self._publish(event)
                outcome = "completed"
        with self._lock:
            self._outcomes[session_id] = outcome

    def _on_notification(
        self,
        notification: Any,
        task_id: str,
        session_id: str,
    ) -> None:
        payload = getattr(notification, "payload", None)
        if not isinstance(payload, dict):
            payload = notification
        method = getattr(notification, "method", None)
        if method == "subagent.started" or method == "subagent.finished":
            for event in map_subagent_notification(payload, task_id=task_id):
                self._publish(event)
            return
        if method == "session.status":
            event = map_session_status(
                str(payload.get("sessionId") or ""),
                str(payload.get("status") or ""),
                task_id=task_id,
            )
            self._publish(event)
            return
        for event in map_session_event(payload, task_id=task_id):
            self._publish(event)

    def _is_cancel_requested(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._cancel_requested

    def request_cancel(self, session_id: str) -> None:
        with self._lock:
            self._cancel_requested.add(session_id)

    def wait_for_turn(self, session_id: str, timeout: float) -> bool:
        thread = self._threads.get(session_id)
        if thread is None:
            return True
        thread.join(timeout=timeout)
        return not thread.is_alive()

    def outcome(self, session_id: str) -> str | None:
        with self._lock:
            return self._outcomes.get(session_id)

    def cancel(self, session_id: str) -> str:
        """协作式取消：等待当前步骤自然结束，超时后终止 Harness 进程。"""
        self.request_cancel(session_id)
        finished = self.wait_for_turn(session_id, timeout=self._shutdown_timeout)
        if not finished:
            self._force_terminate()
            self.wait_for_turn(session_id, timeout=1.0)
        return self.outcome(session_id) or "cancelled"

    def _force_terminate(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001 —— 终止路径不因 close 异常而失败
                pass

    def answer_approval(self, session_id: str, request_id: str, approve: bool) -> None:
        """把审批决定写入 cordis 插件 inbox（与 Spike 的 lumimate-approval-bridge 通道一致）。"""
        if self._approval_inbox is None:
            raise RuntimeError("approval inbox 未配置")
        key = self._approval_key(session_id, request_id)
        self._approval_inbox.mkdir(parents=True, exist_ok=True)
        decision_path = self._approval_inbox / f"{key}.decision.json"
        decision_path.write_text(
            json.dumps({"decision": "allow" if approve else "reject"}),
            encoding="utf-8",
        )

    @staticmethod
    def _approval_key(session_id: str, request_id: str) -> str:
        base = re.sub(r"[^A-Za-z0-9_-]", "_", str(request_id or ""))
        return f"{session_id}__{base}" if base else str(session_id)

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass








