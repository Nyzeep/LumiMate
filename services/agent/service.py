"""Agent 编排服务：Task 状态机、Session 投影与 Bridge 的粘合层。"""

from __future__ import annotations

import threading
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from services.agent.bridge.session_manager import SessionManager
from services.agent.events import build_agent_event
from services.agent.models import SessionProjection, Task
from services.agent.memory import MemoryError
from services.agent.permissions import RiskLevel
from services.agent.tools.authorization import (
    PendingTool,
    ToolAuthorizationGate,
    ToolCall,
    ToolDecision,
)
from services.agent.state_machine import (
    TERMINAL_STATES,
    IllegalTransitionError,
    TaskState,
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
        self._pending_tools: dict[tuple[str, str], PendingTool] = {}
        self._lock = threading.RLock()
        from services.agent.permissions import PermissionPolicy

        self._policy = policy if policy is not None else PermissionPolicy()
        self._authorization = ToolAuthorizationGate(self._policy)
        self._projections = projections
        self._memory = memory
        for task in self._store.load_all().values():
            self._store.save(task)
        if projections is not None:
            self._sessions.restore_projections(
                list(projections.load_all().values())
            )
        bridge.publisher = self._on_bridge_event
        bridge.tool_call_handler = self._on_bridge_tool_call

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
            task.transition_to(TaskState.PLANNING)
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
                task.transition_to(TaskState.RUNNING)
                self._save_and_publish(task, "agent.task.running")
                self._bridge.run_task(task.session_id, task.id, task.goal)
            else:
                task.transition_to(TaskState.CANCELLED)
                self._clear_task_authorization(task.id)
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
            if current.state in (TaskState.RUNNING, TaskState.AWAITING_PERMISSION):
                current.transition_to(TaskState.PAUSED)
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
                task.transition_to(TaskState.CANCELLED)
                self._clear_task_authorization(task.id)
                self._save_and_publish(task, "agent.task.cancelled")
                return task
            if task.state != TaskState.CANCELLING:
                task.transition_to(TaskState.CANCELLING)
                self._store.save(task)
            self._intents[task.session_id] = "cancel"
        self._bridge.cancel(task.session_id)
        with self._lock:
            current = self.get_task(task_id)
            if current.state == TaskState.CANCELLING:
                current.transition_to(TaskState.CANCELLED)
                self._clear_task_authorization(current.id)
                self._save_and_publish(current, "agent.task.cancelled")
            return current

    def close(self) -> None:
        self._bridge.close()

    def resume_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"未知 taskId：{task_id}")
        with self._lock:
            task.transition_to(TaskState.RUNNING)
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
            pending_key = (task.id, request_id)
            pending = self._pending_tools.get(pending_key)
            if pending is None:
                raise ValueError(f"未知权限请求：{request_id}")
            if grant_category != pending.decision.category:
                raise ValueError("权限类别与待确认操作不匹配")
            if approve:
                if pending.decision.level is RiskLevel.MEDIUM:
                    self._policy.grant(
                        task_id=task.id,
                        session_id=task.session_id,
                        workspace=task.workspace,
                        category=pending.decision.category,
                    )
                task.transition_to(TaskState.RUNNING)
                self._save_and_publish(task, "agent.task.running")
                self._pending_tools.pop(pending_key, None)
                self._publish(self._authorization.project_started(pending.call))
            else:
                task.transition_to(TaskState.CANCELLED)
                self._clear_task_authorization(task.id)
                self._save_and_publish(task, "agent.task.cancelled")
            self._bridge.answer_approval(task.session_id, request_id, approve)
            return task

    def _on_bridge_tool_call(
        self,
        notification: dict[str, Any],
        task_id: str,
    ) -> bool:
        call = self._authorization.from_wire(notification, task_id=task_id)
        if call is None:
            return False
        self._handle_tool_call(call)
        return True

    def _handle_tool_call(self, call: ToolCall) -> None:
        task = self.get_task(call.task_id)
        if task is None:
            return
        public_event = self._authorization.project_started(call)
        decision = self._authorization.decide(
            call,
            workspace=task.workspace,
            expected_session_id=str(task.session_id or ""),
        )
        if task.state != TaskState.RUNNING:
            with self._lock:
                duplicate_pending = (
                    task.state == TaskState.AWAITING_PERMISSION
                    and (task.id, call.call_id) in self._pending_tools
                )
            if duplicate_pending:
                return
            if decision.kind != "reject":
                decision = ToolDecision(
                    kind="reject",
                    level=decision.level or RiskLevel.HIGH,
                    category=decision.category,
                    reason="任务当前不接受工具调用",
                )
            self._publish(self._authorization.project_rejected(call, decision))
            return
        if decision.kind == "reject":
            self._publish(self._authorization.project_rejected(call, decision))
            return
        if decision.kind == "allow":
            self._publish(public_event)
            return
        with self._lock:
            task.transition_to(TaskState.AWAITING_PERMISSION)
            self._pending_tools[(task.id, call.call_id)] = PendingTool(call, decision)
            self._store.save(task)
            self._sync_projection(task)
            self._publish(self._authorization.project_permission(call, decision))

    # ---- Bridge 事件回流 ----


    def on_bridge_event(self, event: dict[str, Any]) -> None:
        """Bridge 事件回流入口（公开别名，供测试与外部接线使用）。"""
        self._on_bridge_event(event)

    def on_bridge_tool_call(
        self,
        notification: dict[str, Any],
        task_id: str,
    ) -> bool:
        """Bridge 工具调用回流入口（公开别名；与 bridge.tool_call_handler 同一接缝）。"""
        return self._on_bridge_tool_call(notification, task_id)

    def _on_bridge_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type", "")
        if event_type in ("agent.task.completed", "agent.task.failed", "agent.task.cancelled"):
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
                    task.transition_to(TaskState.AWAITING_PLAN_APPROVAL)
                    task.plan = plan
                    self._save_and_publish(task, "agent.task.awaiting_plan_approval", plan=plan)
                elif task.state == TaskState.RUNNING:
                    task.transition_to(TaskState.COMPLETED)
                    self._clear_task_authorization(task.id)
                    self._save_and_publish(task, "agent.task.completed")
            elif event_type == "agent.task.failed":
                if task.state in (TaskState.PLANNING, TaskState.RUNNING, TaskState.CANCELLING):
                    task.transition_to(TaskState.FAILED)
                    self._clear_task_authorization(task.id)
                    self._save_and_publish(task, "agent.task.failed", failure=event.get("failure"))
            elif event_type == "agent.task.cancelled":
                intent = self._intents.pop(session_id, "cancel")
                if intent == "pause" and task.state in (
                    TaskState.RUNNING,
                    TaskState.AWAITING_PERMISSION,
                    TaskState.PAUSED,
                ):
                    if task.state != TaskState.PAUSED:
                        task.transition_to(TaskState.PAUSED)
                        self._save_and_publish(task, "agent.task.paused")
                elif task.state not in TERMINAL_STATES:
                    task.transition_to(TaskState.CANCELLED)
                    self._clear_task_authorization(task.id)
                    self._save_and_publish(task, "agent.task.cancelled")
                elif task.state == TaskState.CANCELLED:
                    self._clear_task_authorization(task.id)

    # ---- 内部 ----

    def _plan_from_result(self, task: Task) -> list[dict[str, Any]] | None:
        text = self._bridge.final_response(task.session_id)
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

    def _clear_task_authorization(self, task_id: str) -> None:
        self._policy.revoke_for_task(task_id)
        stale = [key for key in self._pending_tools if key[0] == task_id]
        for key in stale:
            self._pending_tools.pop(key, None)

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











