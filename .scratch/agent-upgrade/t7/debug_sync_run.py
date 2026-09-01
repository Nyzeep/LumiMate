"""Direct public-SDK Harness turn probe with safe, structured failure output."""

from __future__ import annotations

import json
import pathlib
import sys
import uuid
from typing import Any

WORKSPACE = pathlib.Path(r"D:\LumiMate")
sys.path.insert(0, str(WORKSPACE))

PROBE_GOAL = "读取 D:\\LumiMate\\README.md 的前 5 行并报告内容；不要修改任何文件。"


def failure_signal(value: Any) -> str:
    """Render only the production allowlisted failure facts for diagnostics."""
    from services.agent.bridge.wire_mapper import (
        failure_from_exception,
        failure_from_turn_reason,
    )

    failure = (
        failure_from_turn_reason(value)
        if isinstance(value, dict)
        else failure_from_exception(RuntimeError(str(value or "")))
    )
    return json.dumps(failure, ensure_ascii=False, sort_keys=True)


def main() -> int:
    from services.agent.runtime import build_harness_client

    harness = None
    signals: list[str] = []
    try:
        harness = build_harness_client(WORKSPACE)
        harness.start()

        def on_notification(notification: Any) -> None:
            method = getattr(notification, "method", "")
            payload = getattr(notification, "payload", {})
            if not isinstance(payload, dict):
                return
            if method == "session.status":
                status = payload.get("status")
                if status:
                    print(f"[probe] session.status={status}", flush=True)
                return
            if method != "session.event":
                return
            event = payload.get("event")
            if not isinstance(event, dict) or event.get("type") != "turn/end":
                return
            data = event.get("data") if isinstance(event.get("data"), dict) else {}
            reason = data.get("reason")
            kind = reason.get("kind") if isinstance(reason, dict) else "unknown"
            if kind == "error":
                signal = failure_signal(reason)
                signals.append(signal)
                print(f"[probe] turn.end kind=error failure={signal}", flush=True)
            else:
                print(f"[probe] turn.end kind={kind}", flush=True)

        result = harness.run(
            PROBE_GOAL,
            session_id=f"task-chamber-probe-{uuid.uuid4().hex}",
            on_notification=on_notification,
        )
        print(f"[probe] finish_reason={result.finish_reason}", flush=True)
        if signals:
            print(
                f"[probe] FAIL Harness emitted an error notification: failure={signals[-1]}",
                flush=True,
            )
            return 1
        if result.finish_reason == "completed":
            print("[probe] PASS real Harness turn completed", flush=True)
            return 0
        detail = failure_signal(result.final_response)
        print(f"[probe] FAIL real Harness turn did not complete: failure={detail}", flush=True)
        return 1
    except Exception as exc:  # noqa: BLE001 - this is an explicit diagnostic probe.
        print(
            f"[probe] FAIL exception={type(exc).__name__} failure={failure_signal(exc)}",
            flush=True,
        )
        return 1
    finally:
        if harness is not None:
            harness.close()


if __name__ == "__main__":
    raise SystemExit(main())
