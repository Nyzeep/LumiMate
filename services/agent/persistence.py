"""Session 投影落盘：只保存投影字段，不复制 Harness 事件日志。"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from services.agent.models import SessionProjection

PROJECTION_FIELDS = frozenset(
    {
        "session_id",
        "task_id",
        "status",
        "title",
        "summary",
        "last_result",
        "resume_index",
    }
)


class ProjectionStore:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)

    def save(self, projection: SessionProjection) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        payload = {
            key: value
            for key, value in asdict(projection).items()
            if key in PROJECTION_FIELDS
        }
        path = self._root / f"{projection.session_id}.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_all(self) -> dict[str, SessionProjection]:
        if not self._root.exists():
            return {}
        projections: dict[str, SessionProjection] = {}
        for path in self._root.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            projection = SessionProjection(**payload)
            projections[projection.session_id] = projection
        return projections
