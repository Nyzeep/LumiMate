"""真实装配冒烟：build_agent_service → start → plan → approve → complete（只读任务）。"""

from __future__ import annotations

import pathlib
import sys
import time

WORKSPACE = pathlib.Path(r"D:\LumiMate")
SPIKE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE))


def main() -> int:
    from services.agent.runtime import build_agent_service
    from services.agent.state_machine import TaskState

    published: list[dict] = []
    service = build_agent_service(WORKSPACE, published.append)
    try:
        task = service.start_task(
            title="真实装配冒烟",
            goal="读取 D:\\LumiMate\\README.md 的前 5 行并报告内容；不要修改任何文件。",
            workspace=str(WORKSPACE),
        )
        print(f"[smoke] task={task.id} session={task.session_id} state={task.state.value}")

        deadline = time.time() + 180
        while time.time() < deadline:
            current = service.get_task(task.id)
            state = current.state
            if state == TaskState.AWAITING_PLAN_APPROVAL:
                print("[smoke] plan ready -> approve")
                service.approve_plan(task.id, approve=True)
            elif state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
                print(f"[smoke] final state={state.value}")
                break
            time.sleep(2)
        else:
            print("[smoke] FAILED — 超时未达终态")
            return 1

        current = service.get_task(task.id)
        if current.state != TaskState.COMPLETED:
            print(f"[smoke] FAILED — state={current.state.value}")
            return 1
        types = [event["type"] for event in published]
        print(f"[smoke] events={types}")
        print(f"[smoke] result={current.result!r}")
        print("[smoke] PASSED")
        return 0
    finally:
        service.close()


if __name__ == "__main__":
    raise SystemExit(main())
