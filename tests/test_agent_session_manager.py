import re

from services.agent.bridge.session_manager import SessionManager


def test_new_session_id_is_generated_when_none():
    manager = SessionManager(root="C:/tmp/sessions")
    first = manager.resolve_session(None)
    second = manager.resolve_session(None)

    assert re.fullmatch(r"session-[0-9a-f]{32}", first)
    assert re.fullmatch(r"session-[0-9a-f]{32}", second)
    assert first != second


def test_provided_session_id_is_reused_for_resume():
    manager = SessionManager(root="C:/tmp/sessions")

    assert manager.resolve_session("s-existing") == "s-existing"
    assert manager.resolve_session("s-unknown") == "s-unknown"


def test_projection_create_and_update_roundtrip(tmp_path):
    manager = SessionManager(root=tmp_path / "sessions")
    manager.resolve_session("s1")
    manager.start_projection("s1", task_id="t1", title="修复测试")
    manager.update_projection("s1", status="running", summary="正在执行")

    projections = manager.list_projections()
    assert len(projections) == 1
    projection = projections[0]
    assert projection.session_id == "s1"
    assert projection.task_id == "t1"
    assert projection.title == "修复测试"
    assert projection.status == "running"
    assert projection.summary == "正在执行"


def test_projection_update_preserves_unrelated_fields(tmp_path):
    manager = SessionManager(root=tmp_path / "sessions")
    manager.resolve_session("s1")
    manager.start_projection("s1", task_id="t1", title="标题")
    manager.update_projection("s1", status="idle")

    projection = manager.list_projections()[0]
    assert projection.title == "标题"
    assert projection.task_id == "t1"


def test_mark_idle_records_resume_index(tmp_path):
    manager = SessionManager(root=tmp_path / "sessions")
    manager.resolve_session("s1")
    manager.start_projection("s1", task_id="t1", title="标题")
    manager.mark_idle("s1", {"messageId": "m1", "turn": 3})

    projection = manager.list_projections()[0]
    assert projection.status == "idle"
    assert projection.resume_index == {"messageId": "m1", "turn": 3}


def test_unknown_session_id_has_no_projection_yet(tmp_path):
    manager = SessionManager(root=tmp_path / "sessions")
    manager.resolve_session("s-unknown")

    assert manager.list_projections() == []
