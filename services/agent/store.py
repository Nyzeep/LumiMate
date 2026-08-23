"""Task 投影的 JSON 落盘与重启恢复。"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from .models import Task
from .state_machine import TERMINAL_STATES, TaskState


class TaskStore:
    """每个 Task 一个 JSON 文件；加载时把非终态任务恢复为 paused + interrupted。"""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    def _path_for(self, task_id: str) -> Path:
        return self._root / f"{task_id}.json"

    def save(self, task: Task) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(task.to_dict(), ensure_ascii=False, indent=2)
        self._path_for(task.id).write_text(payload, encoding="utf-8")

    def load_all(self, *, recover: bool = True) -> dict[str, Task]:
        if not self._root.exists():
            return {}
        tasks: dict[str, Task] = {}
        for path in self._root.glob("*.json"):
            task = Task.from_dict(json.loads(path.read_text(encoding="utf-8")))
            tasks[task.id] = self._recover(task) if recover else task
        return tasks

    def _recover(self, task: Task) -> Task:
        if task.state in TERMINAL_STATES:
            return task
        return replace(task, state=TaskState.PAUSED, interrupted=True)

