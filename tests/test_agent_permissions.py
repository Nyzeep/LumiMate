import pytest

from services.agent.permissions import (
    MEDIUM_CATEGORIES,
    PermissionPolicy,
    RiskLevel,
    classify_action,
)


def test_low_risk_actions_are_automatic():
    for action in ("read", "read_image", "search", "grep", "git_status", "plan", "todo", "list"):
        assert classify_action(action) == RiskLevel.LOW


def test_medium_risk_actions_map_to_categories():
    for action in ("write", "edit"):
        assert classify_action(action) == RiskLevel.MEDIUM
    for action in ("test", "lint", "typecheck"):
        assert classify_action(action) == RiskLevel.MEDIUM


def test_high_risk_actions_always_ask():
    for action in (
        "delete",
        "remove",
        "dependency_modify",
        "config_modify",
        "install",
        "network",
        "system_program",
        "system_settings",
    ):
        assert classify_action(action) == RiskLevel.HIGH


def test_write_outside_workspace_is_high():
    assert (
        classify_action(
            "write",
            path=r"C:\Outside\a.py",
            workspace=r"D:\LumiMate",
        )
        == RiskLevel.HIGH
    )


def test_write_inside_workspace_stays_medium():
    assert (
        classify_action(
            "write",
            path=r"D:\LumiMate\services\a.py",
            workspace=r"D:\LumiMate",
        )
        == RiskLevel.MEDIUM
    )


def test_bash_whitelisted_check_commands_are_medium():
    for command in (
        "python -m pytest",
        "npm run build",
        "python runtime/server.py --check",
        "pytest tests/test_x.py",
    ):
        assert classify_action("bash", command=command) == RiskLevel.MEDIUM


def test_bash_high_risk_commands_are_high():
    for command in (
        "pip install requests",
        "rm -rf x",
        "curl https://example.com",
        "start notepad.exe",
        "npm install left-pad",
    ):
        assert classify_action("bash", command=command) == RiskLevel.HIGH


def test_medium_grant_allows_same_category_within_task():
    policy = PermissionPolicy()
    policy.grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")

    assert (
        policy.check(
            task_id="t1",
            session_id="s1",
            workspace=r"D:\LumiMate",
            action="write",
        )[1]
        == "allow"
    )


def test_medium_without_grant_asks():
    policy = PermissionPolicy()
    assert (
        policy.check(
            task_id="t1",
            session_id="s1",
            workspace=r"D:\LumiMate",
            action="write",
        )[1]
        == "ask"
    )


def test_cross_category_requires_new_grant():
    policy = PermissionPolicy()
    policy.grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")

    assert (
        policy.check(
            task_id="t1",
            session_id="s1",
            workspace=r"D:\LumiMate",
            action="test",
        )[1]
        == "ask"
    )


def test_grant_does_not_cross_tasks():
    policy = PermissionPolicy()
    policy.grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")

    assert (
        policy.check(
            task_id="t2",
            session_id="s1",
            workspace=r"D:\LumiMate",
            action="write",
        )[1]
        == "ask"
    )


def test_grant_does_not_cross_workspace():
    policy = PermissionPolicy()
    policy.grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")

    assert (
        policy.check(
            task_id="t1",
            session_id="s1",
            workspace=r"D:\Other",
            action="write",
        )[1]
        == "ask"
    )


def test_high_never_auto_allows():
    policy = PermissionPolicy()
    level, decision = policy.check(
        task_id="t1",
        session_id="s1",
        workspace=r"D:\LumiMate",
        action="delete",
    )
    assert level == RiskLevel.HIGH
    assert decision == "ask"


def test_revoke_for_task_invalidates_grants():
    policy = PermissionPolicy()
    policy.grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")
    policy.grant(task_id="t2", session_id="s1", workspace=r"D:\LumiMate", category="file_modify")

    policy.revoke_for_task("t1")

    assert (
        policy.check(
            task_id="t1",
            session_id="s1",
            workspace=r"D:\LumiMate",
            action="write",
        )[1]
        == "ask"
    )
    assert (
        policy.check(
            task_id="t2",
            session_id="s1",
            workspace=r"D:\LumiMate",
            action="write",
        )[1]
        == "allow"
    )


def test_grant_rejects_high_category():
    policy = PermissionPolicy()
    with pytest.raises(ValueError):
        policy.grant(task_id="t1", session_id="s1", workspace=r"D:\LumiMate", category="network")


def test_no_auto_escalation_parameters_accepted():
    policy = PermissionPolicy()
    with pytest.raises(TypeError):
        policy.grant(
            task_id="t1",
            session_id="s1",
            workspace=r"D:\LumiMate",
            category="file_modify",
            trust_score=0.9,
        )
    with pytest.raises(TypeError):
        policy.check(
            task_id="t1",
            session_id="s1",
            workspace=r"D:\LumiMate",
            action="write",
            relationship="companion",
        )


def test_medium_categories_match_spec():
    assert MEDIUM_CATEGORIES == frozenset({"file_modify", "test", "lint", "typecheck"})
