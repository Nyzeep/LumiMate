"""调试：走真实 AgentService/Bridge 链路，轮询 outcome/last_result/任务状态。"""

from __future__ import annotations

import pathlib
import sys
import threading
import time

WORKSPACE = pathlib.Path(r"D:\LumiMate")
sys.path.insert(0, str(WORKSPACE))


def main() -> int:
    from services.agent.runtime import build_agent_service
    from services.agent.state_machine import TaskState

    def dump_thread_exception(args):
        import traceback

        print(
            "[debug] thread exception:\n"
            + "".join(
                traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
            ),
            file=sys.stderr,
            flush=True,
        )
    threading.excepthook = dump_thread_exception
    published: list[dict] = []
    import traceback

    original_on_event = None
    service = build_agent_service(WORKSPACE, published.append)
    original_on_event = service._on_bridge_event

    def tracing(event):
        print(
            f"[debug] service got {event.get(chr(34)+chr(116)+chr(121)+chr(112)+chr(101)+chr(34))} taskId={event.get(chr(34)+chr(116)+chr(97)+chr(115)+chr(107)+chr(73)+chr(100)+chr(34))}",
            flush=True,
        )
        try:
            original_on_event(event)
        except Exception:
            traceback.print_exc()
        print(f"[debug] after event published={len(published)}", flush=True)

    service._bridge.publisher = tracing
    try:
        task = service.start_task(
            title="桥接路径调试",
            goal="读取 D:\\LumiMate\\README.md 的前 5 行并报告内容；不要修改任何文件。",
            workspace=str(WORKSPACE),
        )
        print(f"[debug] task={task.id} session={task.session_id}", flush=True)
        deadline = time.time() + 90
        while time.time() < deadline:
            outcome = service._bridge.outcome(task.session_id)
            last_result = service._bridge.last_result(task.session_id)
            current = service.get_task(task.id)
            print(
                f"[debug] state={current.state.value} "
                f"outcome={outcome} last_result={'yes' if last_result else 'no'} "
                f"published={len(published)}",
                flush=True,
            )
            if current.state in (
                TaskState.AWAITING_PLAN_APPROVAL,
                TaskState.COMPLETED,
                TaskState.FAILED,
                TaskState.CANCELLED,
            ):
                print("[debug] reached target state", flush=True)
                print(
                    f"[debug] events={[e['type'] for e in published]}",
                    flush=True,
                )
                print("[debug] PASSED", flush=True)
                return 0
            time.sleep(3)
        print("[debug] FAILED — 超时", flush=True)
        print(f"[debug] events={[e['type'] for e in published]}", flush=True)
        return 1
    finally:
        service.close()


if __name__ == "__main__":
    raise SystemExit(main())
