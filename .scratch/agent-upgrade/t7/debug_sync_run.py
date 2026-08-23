"""调试：同步调用真实 harness.run，打印通知流，定位 idle 是否到达。"""

from __future__ import annotations

import pathlib
import sys
import threading
import time

WORKSPACE = pathlib.Path(r"D:\LumiMate")
sys.path.insert(0, str(WORKSPACE))


def main() -> int:
    from services.agent.runtime import build_agent_service

    def dump_thread_exception(args):
        print(
            f"[debug] thread {args.thread.name} raised: "
            f"{args.exc_type.__name__}: {args.exc_value}",
            file=sys.stderr,
        )

    threading.excepthook = dump_thread_exception
    service = build_agent_service(WORKSPACE, lambda _event: None)
    factory = service._bridge._client_factory
    harness = factory()
    try:
        harness.start()
        seen: list[str] = []

        def on_notification(notification):
            seen.append(notification.method)
            if notification.method == "session.event":
                event = notification.payload.get("event", {})
                print(
                    f"[debug] {notification.method} {event.get('type')}",
                    flush=True,
                )
            else:
                print(f"[debug] {notification.method} {notification.payload}", flush=True)

        result = harness.run(
            "读取 D:\\LumiMate\\README.md 的前 5 行并报告内容；不要修改任何文件。",
            session_id="debug-sync-run",
            on_notification=on_notification,
        )
        print(f"[debug] finish_reason={result.finish_reason}", flush=True)
        print(f"[debug] final_response={result.final_response!r}", flush=True)
        print("[debug] PASSED", flush=True)
        return 0
    finally:
        harness.close()


if __name__ == "__main__":
    raise SystemExit(main())
