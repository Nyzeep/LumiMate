import json
import threading
import pytest
from types import SimpleNamespace

from services.agent.bridge.harness_bridge import HarnessBridge


class FakeHarness:
    def __init__(self, hold: bool = False, run_raised: Exception | None = None):
        self.started = False
        self.closed = False
        self.hold = hold
        self.release = threading.Event()
        self.in_run = threading.Event()
        self.run_raised = run_raised
        self.captured_notifications: list[dict] = []
        self.run_thread: threading.Thread | None = None

    def start(self) -> None:
        self.started = True

    def run(self, prompt: str, session_id: str | None = None, on_notification=None):
        self.run_thread = threading.current_thread()
        self.in_run.set()
        if self.hold:
            self.release.wait(timeout=5)
        if on_notification is not None and session_id:
            on_notification(
                {
                    "sessionId": session_id,
                    "event": {
                        "type": "tool/call",
                        "data": {"callId": "call-1", "name": "write"},
                    },
                }
            )
        if self.run_raised is not None:
            raise self.run_raised
        return SimpleNamespace(finish_reason="completed", final_response="ok")

    def close(self) -> None:
        self.closed = True
        self.release.set()


def make_bridge(fake: FakeHarness, shutdown_timeout: float = 0.2) -> tuple[HarnessBridge, list[dict]]:
    published: list[dict] = []
    bridge = HarnessBridge(
        lambda: fake,
        publisher=published.append,
        shutdown_timeout_seconds=shutdown_timeout,
    )
    return bridge, published


def test_start_initializes_client():
    fake = FakeHarness()
    bridge, _ = make_bridge(fake)
    bridge.start()
    assert fake.started is True


def test_run_executes_on_background_thread():
    fake = FakeHarness()
    bridge, published = make_bridge(fake)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")

    assert fake.in_run.wait(timeout=2) is True
    assert fake.run_thread is not threading.current_thread()
    assert bridge.wait_for_turn("s1", timeout=2) is True
    assert bridge.outcome("s1") == "completed"
    assert any(event["type"] == "agent.task.completed" for event in published)


def test_run_publishes_mapped_wire_events():
    fake = FakeHarness()
    bridge, published = make_bridge(fake)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    tool_event = next(event for event in published if event["type"] == "agent.task.tool_started")
    assert tool_event["toolName"] == "write"
    assert tool_event["taskId"] == "t1"
    assert tool_event["sessionId"] == "s1"


def test_cancel_waits_for_current_step_then_cancels_gracefully():
    fake = FakeHarness(hold=True)
    bridge, published = make_bridge(fake, shutdown_timeout=2.0)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")
    assert fake.in_run.wait(timeout=2) is True

    result_holder: list[str] = []

    def request_cancel():
        result_holder.append(bridge.cancel("s1"))

    canceller = threading.Thread(target=request_cancel)
    canceller.start()
    threading.Event().wait(0.05)
    fake.release.set()
    canceller.join(timeout=3)

    assert result_holder == ["cancelled"]
    assert fake.closed is False
    assert any(event["type"] == "agent.task.cancelled" for event in published)


def test_cancel_times_out_and_terminates_process():
    fake = FakeHarness(hold=True)
    bridge, published = make_bridge(fake, shutdown_timeout=0.1)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")
    assert fake.in_run.wait(timeout=2) is True

    result = bridge.cancel("s1")

    assert result == "cancelled"
    assert fake.closed is True
    assert any(event["type"] == "agent.task.cancelled" for event in published)


def test_run_failure_emits_failed_event():
    fake = FakeHarness(run_raised=RuntimeError("boom"))
    bridge, published = make_bridge(fake)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    assert bridge.outcome("s1") == "failed"
    failed = next(event for event in published if event["type"] == "agent.task.failed")
    assert failed["failure"] == {"reason": "error"}


def test_run_result_error_marks_bridge_outcome_failed():
    class ErrorHarness(FakeHarness):
        def run(self, *_args, **_kwargs):
            return SimpleNamespace(finish_reason="error", final_response="", events=[])

    bridge, published = make_bridge(ErrorHarness())
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    assert bridge.outcome("s1") == "failed"
    assert any(event["type"] == "agent.task.failed" for event in published)


def test_notification_failure_wins_over_inconsistent_completed_result():
    class InconsistentHarness(FakeHarness):
        def run(self, _prompt, session_id=None, on_notification=None):
            if on_notification is not None and session_id:
                on_notification(
                    {
                        "sessionId": session_id,
                        "event": {
                            "type": "turn/end",
                            "data": {
                                "reason": {
                                    "kind": "error",
                                    "error": {"code": "AUTH", "status": 401},
                                }
                            },
                        },
                    }
                )
            return SimpleNamespace(finish_reason="completed", final_response="ok")

    bridge, published = make_bridge(InconsistentHarness())
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    assert bridge.outcome("s1") == "failed"
    terminal_events = [
        event for event in published if event["type"] in {"agent.task.completed", "agent.task.failed"}
    ]
    assert terminal_events == [
        {
            "type": "agent.task.failed",
            "taskId": "t1",
            "sessionId": "s1",
            "failure": {
                "reason": "AUTH",
                "status": 401,
                "message": "Authentication failed (HTTP 401)",
            },
        }
    ]


def test_terminal_deduplication_tracks_each_turn_in_a_session():
    class TwoTurnHarness(FakeHarness):
        def run(self, _prompt, session_id=None, on_notification=None):
            if on_notification is not None and session_id:
                on_notification(
                    {
                        "sessionId": session_id,
                        "event": {
                            "type": "turn/end",
                            "data": {"reason": {"kind": "completed"}},
                        },
                    }
                )
            return SimpleNamespace(finish_reason="completed", final_response="ok")

    bridge, published = make_bridge(TwoTurnHarness())
    bridge.start()

    bridge.run_task(session_id="s1", task_id="t1", goal="plan")
    assert bridge.wait_for_turn("s1", timeout=2) is True
    bridge.run_task(session_id="s1", task_id="t1", goal="execute")
    assert bridge.wait_for_turn("s1", timeout=2) is True

    terminal_events = [event for event in published if event["type"] == "agent.task.completed"]
    assert len(terminal_events) == 2
    assert bridge.outcome("s1") == "completed"


def test_terminal_deduplication_isolated_between_overlapping_turns():
    class OverlappingHarness(FakeHarness):
        def __init__(self):
            super().__init__()
            self.first_started = threading.Event()
            self.second_started = threading.Event()
            self.release = threading.Event()

        def run(self, prompt, session_id=None, on_notification=None):
            if prompt == "first":
                self.first_started.set()
            else:
                self.second_started.set()
            self.release.wait(timeout=2)
            if on_notification is not None and session_id:
                on_notification(
                    {
                        "sessionId": session_id,
                        "event": {
                            "type": "turn/end",
                            "data": {"reason": {"kind": "completed"}},
                        },
                    }
                )
            return SimpleNamespace(finish_reason="completed", final_response="ok")

    harness = OverlappingHarness()
    bridge, published = make_bridge(harness)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="first")
    assert harness.first_started.wait(timeout=2)
    bridge.run_task(session_id="s1", task_id="t1", goal="second")
    assert harness.second_started.wait(timeout=2)

    harness.release.set()
    for _ in range(100):
        terminal_events = [event for event in published if event["type"] == "agent.task.completed"]
        if len(terminal_events) == 2:
            break
        threading.Event().wait(timeout=0.01)

    assert len([event for event in published if event["type"] == "agent.task.completed"]) == 2


def test_terminal_deduplication_tracks_delayed_first_turn_notification():
    class OutOfOrderHarness(FakeHarness):
        def __init__(self):
            super().__init__()
            self.first_started = threading.Event()
            self.allow_first_to_finish = threading.Event()

        def run(self, prompt, session_id=None, on_notification=None):
            if prompt == "first":
                self.first_started.set()
                self.allow_first_to_finish.wait(timeout=2)
                if on_notification is not None and session_id:
                    on_notification(
                        {
                            "sessionId": session_id,
                            "event": {
                                "type": "turn/end",
                                "data": {"reason": {"kind": "error"}},
                            },
                        }
                    )
                return SimpleNamespace(finish_reason="completed", final_response="stale")
            return SimpleNamespace(finish_reason="completed", final_response="second")

    harness = OutOfOrderHarness()
    bridge, published = make_bridge(harness)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="first")
    assert harness.first_started.wait(timeout=2)
    bridge.run_task(session_id="s1", task_id="t1", goal="second")
    assert bridge.wait_for_turn("s1", timeout=2) is True

    harness.allow_first_to_finish.set()
    for _ in range(100):
        terminal_events = [
            event
            for event in published
            if event["type"] in {"agent.task.completed", "agent.task.failed"}
        ]
        if len(terminal_events) == 2:
            break
        threading.Event().wait(timeout=0.01)

    assert [event["type"] for event in terminal_events] == [
        "agent.task.completed",
        "agent.task.failed",
    ]


def test_run_exception_preserves_a_redacted_auth_failure_signal():
    fake = FakeHarness(run_raised=RuntimeError("AUTH HTTP 401 api key: sk-test-credential"))
    bridge, published = make_bridge(fake)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="执行任务")

    assert bridge.wait_for_turn("s1", timeout=2) is True
    failed = next(event for event in published if event["type"] == "agent.task.failed")
    assert failed["failure"] == {
        "reason": "AUTH",
        "status": 401,
        "message": "Authentication failed (HTTP 401)",
    }


def test_close_closes_client():
    fake = FakeHarness()
    bridge, _ = make_bridge(fake)
    bridge.start()
    bridge.close()
    assert fake.closed is True


def test_answer_approval_writes_allow_decision(tmp_path):
    bridge = HarnessBridge(
        lambda: FakeHarness(),
        publisher=lambda _event: None,
        shutdown_timeout_seconds=0.2,
        approval_inbox=tmp_path / "inbox",
    )

    bridge.answer_approval("s1", "call-1", True)

    decision = json.loads(
        (tmp_path / "inbox" / "s1__call-1.decision.json").read_text(encoding="utf-8")
    )
    assert decision == {"decision": "allow"}


def test_answer_approval_writes_reject_decision(tmp_path):
    bridge = HarnessBridge(
        lambda: FakeHarness(),
        publisher=lambda _event: None,
        shutdown_timeout_seconds=0.2,
        approval_inbox=tmp_path / "inbox",
    )

    bridge.answer_approval("s1", "call-1", False)

    decision = json.loads(
        (tmp_path / "inbox" / "s1__call-1.decision.json").read_text(encoding="utf-8")
    )
    assert decision == {"decision": "reject"}


def test_answer_approval_without_inbox_raises():
    bridge = HarnessBridge(lambda: FakeHarness(), publisher=lambda _event: None)
    with pytest.raises(RuntimeError):
        bridge.answer_approval("s1", "call-1", True)


def test_run_task_auto_starts_client():
    fake = FakeHarness()
    bridge = HarnessBridge(lambda: fake, publisher=lambda _event: None)
    bridge.run_task(session_id="s1", task_id="t1", goal="任务")
    assert fake.started is True
    assert bridge.wait_for_turn("s1", timeout=2) is True


def test_run_stores_result_for_last_result():
    fake = FakeHarness()
    bridge, _ = make_bridge(fake)
    bridge.start()
    bridge.run_task(session_id="s1", task_id="t1", goal="任务")
    assert bridge.wait_for_turn("s1", timeout=2) is True
    result = bridge.last_result("s1")
    assert result is not None
    assert result.finish_reason == "completed"
