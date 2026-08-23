from services.agent.models import Grant, Task
from services.agent.state_machine import TaskState
from services.agent.store import TaskStore


def test_grant_carries_four_tuple_fields():
    first = Grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")
    same = Grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")
    other_category = Grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="test")

    assert first.task_id == "t1"
    assert first.session_id == "s1"
    assert first.workspace == r"D:\LumiMate"
    assert first.category == "file_modify"
    assert first == same
    assert first != other_category


def test_task_roundtrip_preserves_all_fields(tmp_path):
    task = Task(
        id="task-1",
        title="修复测试失败",
        state=TaskState.COMPLETED,
        workspace=r"D:\LumiMate",
        goal="让 pytest 全绿",
        session_id="s1",
        plan=[{"step": "读代码"}],
        summary="进行中",
        result=None,
        failure=None,
        interrupted=False,
    )

    store = TaskStore(tmp_path)
    store.save(task)
    loaded = store.load_all()["task-1"]

    assert loaded == task
    assert loaded.state == TaskState.COMPLETED
    assert loaded.plan == [{"step": "读代码"}]


def test_load_all_returns_multiple_tasks(tmp_path):
    store = TaskStore(tmp_path)
    store.save(Task(id="a", title="甲", state=TaskState.DRAFT))
    store.save(Task(id="b", title="乙", state=TaskState.PLANNING))

    assert set(store.load_all()) == {"a", "b"}


def test_non_terminal_tasks_recover_to_paused_interrupted(tmp_path):
    store = TaskStore(tmp_path)
    non_terminal = [
        TaskState.DRAFT,
        TaskState.PLANNING,
        TaskState.AWAITING_PLAN_APPROVAL,
        TaskState.AWAITING_PERMISSION,
        TaskState.RUNNING,
        TaskState.PAUSED,
        TaskState.CANCELLING,
    ]
    for state in non_terminal:
        store.save(Task(id=state.value, title="x", state=state))

    loaded = store.load_all()

    for state in non_terminal:
        task = loaded[state.value]
        assert task.state == TaskState.PAUSED
        assert task.interrupted is True


def test_terminal_tasks_keep_state_after_reload(tmp_path):
    store = TaskStore(tmp_path)
    terminal = [TaskState.CANCELLED, TaskState.COMPLETED, TaskState.FAILED]
    for state in terminal:
        store.save(Task(id=state.value, title="x", state=state))

    loaded = store.load_all()

    for state in terminal:
        task = loaded[state.value]
        assert task.state == state
        assert task.interrupted is False


def test_load_all_on_missing_root_returns_empty(tmp_path):
    store = TaskStore(tmp_path / "not-created-yet")
    assert store.load_all() == {}

