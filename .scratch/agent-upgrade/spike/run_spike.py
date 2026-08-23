"""LumiMate x Harness Spike：Windows 上 Python SDK + dev node 载体受控任务闭环。"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import threading
import time
import uuid

SPIKE_DIR = pathlib.Path(__file__).resolve().parent
WORKSPACE = pathlib.Path(r"D:\LumiMate")
SESSION_ROOT = SPIKE_DIR / "sessions"
INBOX = SPIKE_DIR / "approval-inbox"
OUTBOX = SPIKE_DIR / "approval-outbox"

# 环境默认值：node 载体 + 受控工作目录 + 审批桥通道（脚本内设置，避免 shell 转义问题）。
os.environ.setdefault("DSH_RUNTIME_MODE", "node")
os.environ.setdefault("DSH_CWD", str(WORKSPACE))
os.environ.setdefault("DSH_SESSION_ROOT", str(SESSION_ROOT))
os.environ.setdefault("DSH_CORDIS_CONFIG", str(SPIKE_DIR / "cordis.yml"))
os.environ.setdefault("DSH_APPROVAL_INBOX", str(INBOX))
os.environ.setdefault("DSH_APPROVAL_OUTBOX", str(OUTBOX))

sys.path.insert(0, str(WORKSPACE))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load_api_key() -> str:
    env_file = WORKSPACE / ".env"
    if env_file.exists():
        for raw in env_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("DEEPSEEK_API_KEY", "")


class AutoApprover:
    """模拟用户审批：发现 ask 文件后写入 allow 决定（Spike 受控场景）。"""

    def __init__(self, inbox: pathlib.Path, outbox: pathlib.Path) -> None:
        self.inbox = inbox
        self.outbox = outbox
        self.asks: list[dict] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=3)

    def _run(self) -> None:
        while not self._stop.is_set():
            if self.outbox.exists():
                for ask_file in sorted(self.outbox.glob("*.ask.json")):
                    try:
                        ask = json.loads(ask_file.read_text(encoding="utf-8"))
                        self.asks.append(ask)
                        key = ask_file.name.replace(".ask.json", "")
                        decision_path = self.inbox / f"{key}.decision.json"
                        self.inbox.mkdir(parents=True, exist_ok=True)
                        decision_path.write_text(
                            json.dumps({"decision": "allow"}), encoding="utf-8"
                        )
                        ask_file.unlink()
                        print(
                            f"[spike] approved: {ask.get('toolName')} "
                            f"callId={ask.get('callId')}"
                        )
                    except Exception as exc:  # noqa: BLE001
                        print(f"[spike] approver error: {exc}")
            time.sleep(0.2)


def normalize(notification) -> dict:
    payload = getattr(notification, "payload", None)
    if isinstance(payload, dict):
        return payload
    if isinstance(notification, dict):
        return notification
    return {}


def main() -> int:
    api_key = load_api_key()
    if not api_key:
        print("spike: DEEPSEEK_API_KEY 未配置")
        return 2

    from deepseek_harness import DeepSeekHarness
    from services.agent.bridge.wire_mapper import map_session_event

    for path in (SESSION_ROOT, INBOX, OUTBOX):
        path.mkdir(parents=True, exist_ok=True)

    approver = AutoApprover(INBOX, OUTBOX)
    approver.start()

    session_id = f"spike-{uuid.uuid4().hex[:12]}"
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    artifact = SPIKE_DIR / "spike-result.txt"

    phase1_goal = (
        "使用文件系统 write 工具在 D:\\LumiMate\\.scratch\\agent-upgrade\\spike "
        "目录创建文件 spike-result.txt，内容为 'LumiMate x Harness spike ok'。"
        "如果 write 因沙箱策略被拒绝，请按工具返回的升级指引重试（提供 sandbox_permissions 与 justification）。"
        "随后使用 bash 运行 D:/LumiMate/.venv/Scripts/python.exe runtime/server.py --check，"
        "确认命令以 exit code 0 成功退出并报告输出。"
    )
    phase2_goal = (
        "使用文件系统 write 工具更新 D:\\LumiMate\\.scratch\\agent-upgrade\\spike\\spike-result.txt："
        "在现有内容后追加一行 'approval loop ok'。"
        "如果 write 因沙箱策略被拒绝，请按工具返回的升级指引重试（提供 sandbox_permissions 与 justification）。"
        "不要修改其他任何文件。"
    )

    results: list[tuple[int, object, list[dict], list[dict]]] = []

    try:
        with DeepSeekHarness(
            provider="deepseek-official",
            model="deepseek-v4-flash",
            api_key=api_key,
            cwd=str(WORKSPACE),
            session_root=str(SESSION_ROOT),
            cordis=str(SPIKE_DIR / "cordis.yml"),
            request_timeout_seconds=240,
            shutdown_timeout_seconds=10,
        ) as harness:
            for index, goal in enumerate((phase1_goal, phase2_goal), start=1):
                turn_payloads: list[dict] = []
                result = harness.run(
                    goal,
                    session_id=session_id,
                    on_notification=lambda notification: turn_payloads.append(
                        normalize(notification)
                    ),
                )
                mapped: list[dict] = []
                for payload in turn_payloads:
                    mapped.extend(map_session_event(payload, task_id=task_id))
                results.append((index, result, mapped, turn_payloads))
    finally:
        approver.stop()

    ok = True
    for index, result, mapped, turn_payloads in results:
        finish = getattr(result, "finish_reason", None)
        final = getattr(result, "final_response", None)
        print(f"\n[spike] turn {index}: finish_reason={finish}")
        print(f"[spike] turn {index}: final_response={final!r}")
        print(f"[spike] turn {index}: mapped_events={[e['type'] for e in mapped]}")
        wire_types = [
            payload.get("event", {}).get("type")
            for payload in turn_payloads
            if isinstance(payload, dict)
        ]
        from collections import Counter

        counts = Counter(wire_types)
        summary = ", ".join(f"{name}x{count}" for name, count in counts.most_common(12))
        print(f"[spike] turn {index}: wire_event_counts={summary}")
        if finish != "completed":
            ok = False

    print(f"\n[spike] session_id={session_id}")
    print(f"[spike] approvals_answered={len(approver.asks)}")
    for ask in approver.asks:
        print(f"[spike] approval ask: tool={ask.get('toolName')} callId={ask.get('callId')}")
    check_result = subprocess.run(
        [sys.executable, "runtime/server.py", "--check"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
    )
    print(f"[spike] whitelist_check_exit={check_result.returncode}")
    print(f"[spike] whitelist_check_stdout={check_result.stdout.strip()!r}")

    print(f"[spike] artifact_exists={artifact.exists()}")
    artifact_text = ""
    if artifact.exists():
        artifact_text = artifact.read_text(encoding="utf-8", errors="replace")
        print(f"[spike] artifact_content={artifact_text!r}")

    if not ok:
        print("spike: FAILED — 存在未完成 turn")
        return 1
    if not artifact.exists():
        print("spike: FAILED — 受控文件未创建")
        return 1
    if len(approver.asks) == 0:
        print("spike: FAILED — 未发生审批问询，审批闭环未验证")
        return 1
    if "approval loop ok" not in artifact_text:
        print("spike: FAILED — 第二阶段 write 更新未完成")
        return 1
    if check_result.returncode != 0:
        print("spike: FAILED — 白名单检查未通过")
        return 1
    print("spike: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

