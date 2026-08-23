import pytest

from services.agent.memory import MemoryError, MemoryStore


def test_propose_creates_pending_proposal(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    proposal = store.propose(summary="用户偏好 pytest", kind="preference", source_task_id="t1")

    assert proposal["status"] == "pending"
    assert proposal["summary"] == "用户偏好 pytest"
    assert proposal["sourceTaskId"] == "t1"
    assert store.list_memories() == []


def test_accept_saves_memory(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    proposal = store.propose(summary="用中文回复", kind="preference")

    store.confirm(proposal["proposalId"], accept=True)

    memories = store.list_memories()
    assert len(memories) == 1
    assert memories[0]["summary"] == "用中文回复"
    assert memories[0]["kind"] == "preference"


def test_reject_never_saves_memory(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    proposal = store.propose(summary="不想要", kind="preference")

    store.confirm(proposal["proposalId"], accept=False)

    assert store.list_memories() == []


def test_unconfirmed_proposal_not_saved(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    store.propose(summary="未确认", kind="preference")

    assert store.list_memories() == []


def test_unknown_proposal_raises(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    with pytest.raises(MemoryError):
        store.confirm("memory-nope", accept=True)


def test_double_confirm_raises(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    proposal = store.propose(summary="x", kind="preference")
    store.confirm(proposal["proposalId"], accept=True)

    with pytest.raises(MemoryError):
        store.confirm(proposal["proposalId"], accept=True)


def test_propose_requires_summary_and_kind(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    with pytest.raises(MemoryError):
        store.propose(summary="", kind="preference")
    with pytest.raises(MemoryError):
        store.propose(summary="x", kind="")


def test_memories_persist_across_store_instances(tmp_path):
    root = tmp_path / "memory"
    first = MemoryStore(root)
    proposal = first.propose(summary="任务摘要", kind="task_summary")
    first.confirm(proposal["proposalId"], accept=True)

    second = MemoryStore(root)
    assert len(second.list_memories()) == 1
