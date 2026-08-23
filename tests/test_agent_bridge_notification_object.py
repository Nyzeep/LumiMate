import threading
from types import SimpleNamespace

from services.agent.bridge.harness_bridge import HarnessBridge


def test_run_publishes_events_from_sdk_notification_objects():
    published: list[dict] = []

    class NotificationHarness:
        started = False
        closed = False
        in_run = threading.Event()

        def start(self):
            self.started = True

        def run(self, prompt, session_id=None, on_notification=None):
            self.in_run.set()
            if on_notification is not None and session_id:
                on_notification(
                    SimpleNamespace(
                        method="session.event",
                        payload={
                            "sessionId": session_id,
                            "event": {
                                "type": "tool/call",
                                "data": {"callId": "call-1", "name": "write"},
                            },
                        },
                    )
                )
            return SimpleNamespace(finish_reason="completed", final_response="ok")

        def close(self):
            self.closed = True

    fake = NotificationHarness()
    bridge = HarnessBridge(lambda: fake, publisher=published.append)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    tool_event = next(
        event for event in published if event["type"] == "agent.task.tool_started"
    )
    assert tool_event["toolName"] == "write"
    assert tool_event["sessionId"] == "s1"


def test_bridge_dispatches_session_status_and_subagent_notifications():
    published: list[dict] = []

    class StatusHarness:
        started = False
        closed = False
        in_run = threading.Event()

        def start(self):
            self.started = True

        def run(self, prompt, session_id=None, on_notification=None):
            self.in_run.set()
            if on_notification is not None and session_id:
                on_notification(
                    SimpleNamespace(
                        method="session.status",
                        payload={"sessionId": session_id, "status": "idle"},
                    )
                )
                on_notification(
                    SimpleNamespace(
                        method="subagent.started",
                        payload={
                            "parentSessionId": session_id,
                            "childSessionId": "child-1",
                        },
                    )
                )
            return SimpleNamespace(finish_reason="completed", final_response="ok")

        def close(self):
            self.closed = True

    fake = StatusHarness()
    bridge = HarnessBridge(lambda: fake, publisher=published.append)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    session_event = next(
        event for event in published if event["type"] == "agent.session.updated"
    )
    assert session_event["sessionId"] == "s1"
    assert session_event["status"] == "idle"
    assert not any(
        event["type"] == "agent.task.tool_started" for event in published
    )


def test_bridge_projects_file_changed_and_test_result(tmp_path):
    from services.agent.tools.normalizer import ToolProjector

    published: list[dict] = []
    workspace = tmp_path / "ws"
    workspace.mkdir()

    class ProjectorHarness:
        started = False
        closed = False
        in_run = threading.Event()

        def start(self):
            self.started = True

        def run(self, prompt, session_id=None, on_notification=None):
            self.in_run.set()
            if on_notification is None or session_id is None:
                return SimpleNamespace(finish_reason="completed", final_response="ok")
            on_notification(
                SimpleNamespace(
                    method="session.event",
                    payload={
                        "sessionId": session_id,
                        "event": {
                            "type": "tool/call",
                            "data": {
                                "callId": "c1",
                                "name": "write",
                                "arguments": '{"file_path": "new.txt", "content": "hi"}',
                            },
                        },
                    },
                )
            )
            (workspace / "new.txt").write_text("hi", encoding="utf-8")
            on_notification(
                SimpleNamespace(
                    method="session.event",
                    payload={
                        "sessionId": session_id,
                        "event": {
                            "type": "tool/result",
                            "data": {
                                "callId": "c1",
                                "message": {"content": [{"type": "text", "text": "ok"}]},
                            },
                        },
                    },
                )
            )
            on_notification(
                SimpleNamespace(
                    method="session.event",
                    payload={
                        "sessionId": session_id,
                        "event": {
                            "type": "tool/call",
                            "data": {
                                "callId": "c2",
                                "name": "bash",
                                "arguments": '{"command": "python -m pytest tests/test_x.py -q"}',
                            },
                        },
                    },
                )
            )
            on_notification(
                SimpleNamespace(
                    method="session.event",
                    payload={
                        "sessionId": session_id,
                        "event": {
                            "type": "tool/result",
                            "data": {
                                "callId": "c2",
                                "message": {
                                    "content": [
                                        {"type": "text", "text": "=== 2 passed in 0.4s ==="}
                                    ]
                                },
                            },
                        },
                    },
                )
            )
            return SimpleNamespace(finish_reason="completed", final_response="ok")

        def close(self):
            self.closed = True

    fake = ProjectorHarness()
    bridge = HarnessBridge(
        lambda: fake,
        publisher=published.append,
        tool_projector=ToolProjector(str(workspace)),
    )
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    file_event = next(
        event for event in published if event["type"] == "agent.task.file_changed"
    )
    assert file_event["path"] == str(workspace / "new.txt")
    assert file_event["operation"] == "create"
    test_event = next(
        event for event in published if event["type"] == "agent.task.test_result"
    )
    assert test_event["passed"] == 2
    assert test_event["failed"] == 0
    assert test_event["durationMs"] == 400
