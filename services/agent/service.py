"""Agent 编排服务：Task 状态机、Session 投影与 Bridge 的粘合层。"""

from __future__ import annotations

import json

import threading
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from services.agent.bridge.session_manager import SessionManager
from services.agent.events import build_agent_event
from services.agent.models import SessionProjection, Task
from services.agent.memory import MemoryError
from services.agent.permissions import MEDIUM_CATEGORIES
from services.agent.tools.registry import is_allowed_tool
from services.agent.state_machine import (
    TERMINAL_STATES,
    IllegalTransitionError,
    TaskState,
    apply_transition,
)
from services.agent.store import TaskStore


class AgentService:
    """持有 Task 生命周期；Bridge 事件经 on_bridge_event 回流并驱动状态转换。"""

    def __init__(
        self,
        *,
        store: TaskStore,
        sessions_root: str | Path,
        bridge: Any,
        publisher: Callable[[dict[str, Any]], None],
        workspace: str,
        policy: Any | None = None,
        projections: Any | None = None,
        memory: Any | None = None,
    ) -> None:
        self._store = store
        self._sessions = SessionManager(sessions_root)
        self._bridge = bridge
        self._publish = publisher
        self._workspace = workspace
        self._intents: dict[str, str] = {}
        self._pending_tools: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()
        from services.agent.permissions import PermissionPolicy

        self._policy = policy if policy is not None else PermissionPolicy()
        self._projections = projections
        self._memory = memory
        for task in self._store.load_all().values():
            self._store.save(task)
        if projections is not None:
            self._sessions.restore_projections(
                list(projections.load_all().values())
            )
        bridge.publisher = self._on_bridge_event

    # ---- 查询 ----

    def get_task(self, task_id: str) -> Task | None:
        with self._lock:
            return self._store.load_all(recover=False).get(task_id)

    def status(self) -> dict[str, Any]:
        with self._lock:
            tasks = self._store.load_all(recover=False)
            non_terminal = [t for t in tasks.values() if t.state not in TERMINAL_STATES]
            current = non_terminal[0] if non_terminal else None
            return {
                "ready": True,
                "harnessAvailable": True,
                "currentTask": current.to_api_dict() if current else None,
                "sessions": [self._projection_dict(p) for p in self._sessions.list_projections()],
            }

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._lock:
            return [self._projection_dict(p) for p in self._sessions.list_projections()]

    # ---- 任务操作 ----

    def start_task(self, title: str, goal: str, workspace: str) -> Task:
        return self._launch_plan_turn(
            session_id=self._sessions.resolve_session(None),
            title=title,
            goal=goal,
            workspace=workspace,
        )

    def resume_session(self, session_id: str, title: str, goal: str, workspace: str) -> Task:
        """以指定 sessionId 恢复：同一 session_root + 同一 sessionId，未知 id 由 Runtime 惰性创建。"""
        return self._launch_plan_turn(
            session_id=self._sessions.resolve_session(session_id),
            title=title,
            goal=goal,
            workspace=workspace,
        )

    def _launch_plan_turn(self, *, session_id: str, title: str, goal: str, workspace: str) -> Task:
        if workspace != self._workspace:
            raise ValueError(f"workspace 必须固定为 {self._workspace}")
        task = Task(
            id=f"task-{uuid.uuid4().hex[:12]}",
            title=title,
            state=TaskState.DRAFT,
            workspace=workspace,
            goal=goal,
            session_id=session_id,
        )
        with self._lock:
            self._save_and_publish(task, "agent.task.created", title=title, state=task.state.value)
            apply_transition(task.state, TaskState.PLANNING)
            task.state = TaskState.PLANNING
            self._save_and_publish(task, "agent.task.planning")
            self._sessions.start_projection(session_id, task.id, title)
            self._bridge.run_task(session_id, task.id, goal)
        return task

    def approve_plan(self, task_id: str, approve: bool) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"未知 taskId：{task_id}")
        with self._lock:
            if approve:
                apply_transition(task.state, TaskState.RUNNING)
                task.state = TaskState.RUNNING
                self._save_and_publish(task, "agent.task.running")
                self._bridge.run_task(task.session_id, task.id, task.goal)
            else:
                apply_transition(task.state, TaskState.CANCELLED)
                task.state = TaskState.CANCELLED
                self._save_and_publish(task, "agent.task.cancelled")
            return task

    def pause_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"未知 taskId：{task_id}")
        with self._lock:
            if task.state not in (TaskState.RUNNING, TaskState.AWAITING_PERMISSION):
                raise IllegalTransition(task)
            self._intents[task.session_id] = "pause"
        self._bridge.cancel(task.session_id)
        with self._lock:
            current = self.get_task(task_id)
            if current.state == TaskState.RUNNING:
                apply_transition(current.state, TaskState.PAUSED)
                current.state = TaskState.PAUSED
                self._save_and_publish(current, "agent.task.paused")
            return current

    def cancel_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"未知 taskId：{task_id}")
        with self._lock:
            if task.state in (TaskState.COMPLETED, TaskState.CANCELLED, TaskState.FAILED):
                return task
            if task.state in (
                TaskState.PLANNING,
                TaskState.AWAITING_PLAN_APPROVAL,
                TaskState.AWAITING_PERMISSION,
                TaskState.PAUSED,
            ):
                apply_transition(task.state, TaskState.CANCELLED)
                task.state = TaskState.CANCELLED
                self._save_and_publish(task, "agent.task.cancelled")
                return task
            if task.state != TaskState.CANCELLING:
                apply_transition(task.state, TaskState.CANCELLING)
                task.state = TaskState.CANCELLING
                self._store.save(task)
            self._intents[task.session_id] = "cancel"
        self._bridge.cancel(task.session_id)
        with self._lock:
            current = self.get_task(task_id)
            if current.state == TaskState.CANCELLING:
                apply_transition(current.state, TaskState.CANCELLED)
                current.state = TaskState.CANCELLED
                self._save_and_publish(current, "agent.task.cancelled")
            return current

    def close(self) -> None:
        self._bridge.close()

    def resume_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"未知 taskId：{task_id}")
        with self._lock:
            apply_transition(task.state, TaskState.RUNNING)
            task.state = TaskState.RUNNING
            self._save_and_publish(task, "agent.task.running")
            self._bridge.run_task(task.session_id, task.id, task.goal)
            return task


    def approve_permission(
        self,
        task_id: str,
        *,
        request_id: str,
        grant_category: str,
        approve: bool,
    ) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"未知 taskId：{task_id}")
        with self._lock:
            if task.state != TaskState.AWAITING_PERMISSION:
                raise IllegalTransition(task)
            if approve:
                if grant_category in MEDIUM_CATEGORIES:
                    self._policy.grant(
                        task_id=task.id,
                        session_id=task.session_id,
                        workspace=task.workspace,
                        category=grant_category,
                    )
                apply_transition(task.state, TaskState.RUNNING)
                task.state = TaskState.RUNNING
                self._save_and_publish(task, "agent.task.running")
                pending = self._pending_tools.pop(request_id, None)
                if pending is not None:
                    self._publish(pending)
            else:
                apply_transition(task.state, TaskState.CANCELLED)
                task.state = TaskState.CANCELLED
                self._save_and_publish(task, "agent.task.cancelled")
                self._pending_tools.pop(request_id, None)
            self._bridge.answer_approval(task.session_id, request_id, approve)
            return task

    def _handle_tool_event(self, event: dict[str, Any]) -> None:
        task_id = event.get("taskId")
        if not task_id:
            return
        task = self.get_task(task_id)
        if task is None:
            return
        if task.state != TaskState.RUNNING:
            self._publish(event)
            return
        arguments = self._parse_arguments(event.get("arguments"))
        if not is_allowed_tool(
            str(event.get("toolName") or ""), arguments
        ):
            self._publish(
                build_agent_event(
                    "agent.task.tool_finished",
                    task_id=task.id,
                    session_id=task.session_id,
                    toolName=str(event.get("toolName") or ""),
                    callId=str(event.get("callId") or ""),
                    status="error",
                    summary="工具不在白名单内",
                )
            )
            return
        path_value = arguments.get("file_path") or arguments.get("path")
        command = arguments.get("command")
        _level, decision = self._policy.check(
            task_id=task.id,
            session_id=task.session_id,
            workspace=task.workspace,
            action=str(event.get("toolName") or ""),
            path=str(path_value) if path_value else None,
            command=str(command) if command else None,
        )
        if decision == "allow":
            self._publish(event)
            return
        call_id = str(event.get("callId") or "")
        from services.agent.permissions import CATEGORY_FOR_ACTION

        category = CATEGORY_FOR_ACTION.get(str(event.get("toolName") or ""), "file_modify")
        with self._lock:
            apply_transition(task.state, TaskState.AWAITING_PERMISSION)
            task.state = TaskState.AWAITING_PERMISSION
            self._save_and_publish(
                task,
                "agent.task.awaiting_permission",
                requestId=call_id,
                category=category,
                toolName=str(event.get("toolName") or ""),
                details={"arguments": arguments},
            )
            self._pending_tools[call_id] = event

    @staticmethod
    def _parse_arguments(raw: Any) -> dict[str, Any]:
        if not isinstance(raw, str) or not raw.strip():
            return {}
        try:
            parsed = json.loads(raw)
        except ValueError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    # ---- Bridge 事件回流 ----


    def on_bridge_event(self, event: dict[str, Any]) -> None:
        """Bridge 事件回流入口（公开别名，供测试与外部接线使用）。"""
        self._on_bridge_event(event)

    def _on_bridge_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type", "")
        if event_type == "agent.task.tool_started":
            self._handle_tool_event(event)
        elif event_type in ("agent.task.completed", "agent.task.failed", "agent.task.cancelled"):
            self._handle_state_event(event)
        else:
            self._publish(event)

    def _handle_state_event(self, event: dict[str, Any]) -> None:
        task_id = event.get("taskId")
        if not task_id:
            return
        task = self.get_task(task_id)
        if task is None:
            return
        event_type = event["type"]
        session_id = task.session_id
        with self._lock:
            if event_type == "agent.task.completed":
                if task.state == TaskState.PLANNING:
                    plan = self._plan_from_result(task)
                    apply_transition(task.state, TaskState.AWAITING_PLAN_APPROVAL)
                    task.state = TaskState.AWAITING_PLAN_APPROVAL
                    task.plan = plan
                    self._save_and_publish(task, "agent.task.awaiting_plan_approval", plan=plan)
                elif task.state == TaskState.RUNNING:
                    apply_transition(task.state, TaskState.COMPLETED)
                    task.state = TaskState.COMPLETED
                    self._save_and_publish(task, "agent.task.completed")
                    self._policy.revoke_for_task(task.id)
            elif event_type == "agent.task.failed":
                if task.state in (TaskState.PLANNING, TaskState.RUNNING, TaskState.CANCELLING):
                    apply_transition(task.state, TaskState.FAILED)
                    task.state = TaskState.FAILED
                    self._save_and_publish(task, "agent.task.failed", failure=event.get("failure"))
                    self._policy.revoke_for_task(task.id)
            elif event_type == "agent.task.cancelled":
                self._policy.revoke_for_task(task.id)
                intent = self._intents.pop(session_id, "cancel")
                if intent == "pause" and task.state in (TaskState.RUNNING, TaskState.PAUSED):
                    if task.state == TaskState.RUNNING:
                        apply_transition(task.state, TaskState.PAUSED)
                        task.state = TaskState.PAUSED
                        self._save_and_publish(task, "agent.task.paused")
                elif task.state not in TERMINAL_STATES:
                    apply_transition(task.state, TaskState.CANCELLED)
                    task.state = TaskState.CANCELLED
                    self._save_and_publish(task, "agent.task.cancelled")

    # ---- 内部 ----

    def _plan_from_result(self, task: Task) -> list[dict[str, Any]] | None:
        result = self._bridge.last_result(task.session_id)
        text = getattr(result, "final_response", "") if result is not None else ""
        return [{"summary": text}] if text else []

    def propose_memory(
        self,
        summary: str,
        kind: str,
        source_task_id: str | None = None,
    ) -> dict[str, Any]:
        if self._memory is None:
            raise MemoryError("memory store 未配置")
        proposal = self._memory.propose(summary, kind, source_task_id)
        self._publish(
            build_agent_event(
                "agent.memory.proposed",
                proposalId=proposal["proposalId"],
                summary=proposal["summary"],
                kind=proposal["kind"],
            )
        )
        return proposal

    def confirm_memory(
        self,
        proposal_id: str,
        accept: bool,
    ) -> dict[str, Any]:
        if self._memory is None:
            raise MemoryError("memory store 未配置")
        return self._memory.confirm(proposal_id, accept)

    def _sync_projection(self, task: Task) -> None:
        if self._projections is None:
            return
        projection = self._sessions.update_projection(
            task.session_id,
            status=task.state.value,
            title=task.title,
            summary=task.summary,
            last_result=task.result,
        )
        if projection is None:
            projection = self._sessions.start_projection(
                task.session_id, task.id, task.title
            )
        self._projections.save(projection)

    def _save_and_publish(
        self,
        task: Task,
        event_type: str,
        **fields: Any,
    ) -> None:
        self._store.save(task)
        self._sync_projection(task)
        self._publish(
            build_agent_event(
                event_type,
                task_id=task.id,
                session_id=task.session_id,
                **fields,
            )
        )

    def _projection_dict(self, projection: SessionProjection) -> dict[str, Any]:
        payload = asdict(projection)
        return {
            "sessionId": payload["session_id"],
            "taskId": payload["task_id"],
            "status": payload["status"],
            "title": payload["title"],
            "summary": payload["summary"],
            "lastResult": payload["last_result"],
            "resumeIndex": payload["resume_index"],
        }


class IllegalTransition(IllegalTransitionError):
    """任务当前状态不允许该操作。"""











