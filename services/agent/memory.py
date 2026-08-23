"""Memory 三步流程：Agent 提议 → 用户确认 → LumiMate 保存。"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


class MemoryError(ValueError):
    """Memory 提议/确认不合法。"""


class MemoryStore:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._proposals_file = self._root / "proposals.json"
        self._memories_file = self._root / "memories.json"

    def propose(
        self,
        summary: str,
        kind: str,
        source_task_id: str | None = None,
    ) -> dict[str, Any]:
        if not summary or not kind:
            raise MemoryError("summary 与 kind 均必填")
        proposals = self._load(self._proposals_file)
        proposal = {
            "proposalId": f"memory-{uuid.uuid4().hex[:12]}",
            "summary": summary,
            "kind": kind,
            "sourceTaskId": source_task_id,
            "status": "pending",
        }
        proposals.append(proposal)
        self._save(self._proposals_file, proposals)
        return proposal

    def confirm(self, proposal_id: str, accept: bool) -> dict[str, Any]:
        proposals = self._load(self._proposals_file)
        proposal = next(
            (item for item in proposals if item["proposalId"] == proposal_id),
            None,
        )
        if proposal is None:
            raise MemoryError(f"未知 proposalId：{proposal_id}")
        if proposal["status"] != "pending":
            raise MemoryError(f"提议已处理：{proposal['status']}")
        proposal["status"] = "accepted" if accept else "rejected"
        self._save(self._proposals_file, proposals)
        if accept:
            memories = self._load(self._memories_file)
            memories.append(
                {
                    "memoryId": proposal["proposalId"],
                    "summary": proposal["summary"],
                    "kind": proposal["kind"],
                    "sourceTaskId": proposal["sourceTaskId"],
                }
            )
            self._save(self._memories_file, memories)
        return proposal

    def list_memories(self) -> list[dict[str, Any]]:
        return self._load(self._memories_file)

    def _load(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else []

    def _save(self, path: Path, items: list[dict[str, Any]]) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
