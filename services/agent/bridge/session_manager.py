"""Session 创建/恢复与投影更新。"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from services.agent.models import SessionProjection


class SessionManager:
    """管理 Session 投影；恢复 = 同一 session_root + 同一 sessionId（未知 id 由 Runtime 惰性创建）。"""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._projections: dict[str, SessionProjection] = {}

    def resolve_session(self, session_id: str | None) -> str:
        if session_id:
            return session_id
        return f"session-{uuid.uuid4().hex}"

    def start_projection(
        self,
        session_id: str,
        task_id: str,
        title: str,
    ) -> SessionProjection:
        projection = SessionProjection(
            session_id=session_id,
            task_id=task_id,
            status="draft",
            title=title,
        )
        self._projections[session_id] = projection
        return projection

    def update_projection(
        self,
        session_id: str,
        **fields: Any,
    ) -> SessionProjection | None:
        projection = self._projections.get(session_id)
        if projection is None:
            return None
        for name, value in fields.items():
            if hasattr(projection, name):
                setattr(projection, name, value)
        return projection

    def mark_idle(
        self,
        session_id: str,
        resume_index: dict[str, Any],
    ) -> SessionProjection | None:
        return self.update_projection(
            session_id,
            status="idle",
            resume_index=resume_index,
        )

    def list_projections(self) -> list[SessionProjection]:
        return list(self._projections.values())
