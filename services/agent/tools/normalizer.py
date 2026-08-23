"""工具结果规范化：file_changed / test_result 派生事件。"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from services.agent.events import build_agent_event


def parse_test_summary(text: str) -> tuple[int, int, int]:
    """从 pytest 输出提取 (passed, failed, duration_ms)；无匹配时归零。"""
    passed = 0
    failed = 0
    duration_ms = 0
    passed_match = re.search(r"(\d+)\s+passed", text)
    if passed_match:
        passed = int(passed_match.group(1))
    failed_match = re.search(r"(\d+)\s+failed", text)
    if failed_match:
        failed = int(failed_match.group(1))
    duration_match = re.search(r"in\s+([\d.]+)\s*s", text)
    if duration_match:
        duration_ms = int(float(duration_match.group(1)) * 1000)
    return passed, failed, duration_ms


def _collect_text(blocks: Any) -> list[str]:
    parts: list[str] = []
    for block in blocks or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            parts.append(str(block.get("text") or ""))
        nested = block.get("content")
        if isinstance(nested, list):
            parts.extend(_collect_text(nested))
        elif isinstance(nested, dict):
            parts.extend(_collect_text([nested]))
    return parts


class ToolProjector:
    """按 callId 跟踪工具调用，在 tool/result 后派生 §8 文件/测试事件。"""

    def __init__(self, workspace: str | Path) -> None:
        self._workspace = Path(workspace)
        self._calls: dict[str, dict[str, Any]] = {}

    def on_tool_call(self, notification: dict[str, Any]) -> None:
        event = notification.get("event") or {}
        data = event.get("data") or {}
        call_id = self._call_id(data)
        if not call_id:
            return
        tool_name = str(data.get("name") or "")
        arguments = self._parse_arguments(data.get("arguments"))
        self._calls[call_id] = {
            "tool": tool_name,
            "args": arguments,
            "operation": self._operation_for(tool_name, arguments),
        }

    def on_tool_result(
        self,
        notification: dict[str, Any],
        *,
        task_id: str,
    ) -> list[dict[str, Any]]:
        event = notification.get("event") or {}
        data = event.get("data") or {}
        call_id = self._call_id(data)
        record = self._calls.pop(call_id, None)
        if record is None or data.get("error"):
            return []
        session_id = str(notification.get("sessionId") or "")
        tool_name = record["tool"]
        arguments = record["args"]
        events: list[dict[str, Any]] = []
        if tool_name in ("write", "edit"):
            raw_path = arguments.get("file_path") or arguments.get("path")
            if raw_path:
                path = self._resolve(str(raw_path))
                events.append(
                    build_agent_event(
                        "agent.task.file_changed",
                        task_id=task_id,
                        session_id=session_id,
                        path=str(path),
                        operation=record["operation"],
                        afterHash=self._hash(path),
                    )
                )
        elif tool_name == "bash":
            command = str(arguments.get("command") or "")
            if "pytest" in command.lower():
                passed, failed, duration_ms = parse_test_summary(
                    self._result_text(data)
                )
                events.append(
                    build_agent_event(
                        "agent.task.test_result",
                        task_id=task_id,
                        session_id=session_id,
                        command=command,
                        passed=passed,
                        failed=failed,
                        durationMs=duration_ms,
                    )
                )
        return events

    @staticmethod
    def _call_id(data: dict[str, Any]) -> str:
        call_id = str(data.get("callId") or "")
        if call_id:
            return call_id
        message = data.get("message")
        if isinstance(message, dict):
            source = message.get("source")
            if isinstance(source, dict):
                call_id = str(source.get("callId") or "")
                if call_id:
                    return call_id
            content = message.get("content") or []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool-result":
                    nested = block.get("toolCallId")
                    if nested:
                        return str(nested)
        return ""

    def _operation_for(self, tool_name: str, arguments: dict[str, Any]) -> str:
        if tool_name not in ("write", "edit"):
            return ""
        raw_path = arguments.get("file_path") or arguments.get("path")
        if not raw_path:
            return ""
        path = self._resolve(str(raw_path))
        if tool_name == "edit" or path.exists():
            return "update"
        return "create"

    def _resolve(self, raw_path: str) -> Path:
        path = Path(raw_path)
        return path if path.is_absolute() else self._workspace / path

    def _hash(self, path: Path) -> str | None:
        try:
            if not path.is_file():
                return None
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return None

    @staticmethod
    def _result_text(data: dict[str, Any]) -> str:
        message = data.get("message") or {}
        return "\n".join(_collect_text(message.get("content") or []))

    @staticmethod
    def _parse_arguments(raw: Any) -> dict[str, Any]:
        if not isinstance(raw, str) or not raw.strip():
            return {}
        try:
            parsed = json.loads(raw)
        except ValueError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
