from services.agent.models import SessionProjection
from services.agent.persistence import ProjectionStore


def test_projection_roundtrip_preserves_fields(tmp_path):
    store = ProjectionStore(tmp_path / "projections")
    projection = SessionProjection(
        session_id="s1",
        task_id="t1",
        status="idle",
        title="修复测试",
        summary="计划已生成",
        last_result={"filesChanged": 1},
        resume_index={"messageId": "m1", "turn": 2},
    )

    store.save(projection)
    loaded = store.load_all()["s1"]

    assert loaded == projection
    assert loaded.resume_index == {"messageId": "m1", "turn": 2}


def test_projection_file_contains_only_projection_fields(tmp_path):
    store = ProjectionStore(tmp_path / "projections")
    projection = SessionProjection(
        session_id="s1",
        task_id="t1",
        status="running",
        title="t",
        summary="",
    )

    store.save(projection)
    raw = (tmp_path / "projections" / "s1.json").read_text(encoding="utf-8")

    for forbidden in ("tools", "events", "fileChanges", "testResults", "permission"):
        assert forbidden not in raw
    for expected in (
        '"session_id"',
        '"task_id"',
        '"status"',
        '"title"',
        '"summary"',
        '"last_result"',
        '"resume_index"',
    ):
        assert expected in raw


def test_load_all_missing_root_returns_empty(tmp_path):
    store = ProjectionStore(tmp_path / "not-created")
    assert store.load_all() == {}


def test_load_all_returns_multiple_projections(tmp_path):
    store = ProjectionStore(tmp_path / "projections")
    store.save(SessionProjection(session_id="s1", task_id="t1", status="idle"))
    store.save(SessionProjection(session_id="s2", task_id="t2", status="running"))

    assert set(store.load_all()) == {"s1", "s2"}
