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
