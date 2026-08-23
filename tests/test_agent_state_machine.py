import pytest

from services.agent.state_machine import (
    IllegalTransitionError,
    TERMINAL_STATES,
    TaskState,
    apply_transition,
    can_transition,
)


# 独立事实来源：提案 §9 允许转换表（手工字面量，不从实现复制）
ALLOWED_TRANSITIONS = {
    (TaskState.DRAFT, TaskState.PLANNING),
    (TaskState.AWAITING_PLAN_APPROVAL, TaskState.RUNNING),
    (TaskState.AWAITING_PLAN_APPROVAL, TaskState.CANCELLED),
    (TaskState.PLANNING, TaskState.AWAITING_PLAN_APPROVAL),
    (TaskState.PLANNING, TaskState.FAILED),
    (TaskState.PLANNING, TaskState.CANCELLED),
    (TaskState.AWAITING_PERMISSION, TaskState.RUNNING),
    (TaskState.AWAITING_PERMISSION, TaskState.CANCELLED),
    (TaskState.AWAITING_PERMISSION, TaskState.PAUSED),
    (TaskState.RUNNING, TaskState.AWAITING_PERMISSION),
    (TaskState.RUNNING, TaskState.PAUSED),
    (TaskState.RUNNING, TaskState.CANCELLING),
    (TaskState.RUNNING, TaskState.COMPLETED),
    (TaskState.RUNNING, TaskState.FAILED),
    (TaskState.CANCELLING, TaskState.CANCELLED),
    (TaskState.CANCELLING, TaskState.FAILED),
    (TaskState.PAUSED, TaskState.RUNNING),
    (TaskState.PAUSED, TaskState.CANCELLED),
}

ALL_STATES = set(TaskState)
ALL_PAIRS = {(current, target) for current in ALL_STATES for target in ALL_STATES}
FORBIDDEN_PAIRS = ALL_PAIRS - ALLOWED_TRANSITIONS


@pytest.mark.parametrize("current,target", sorted(ALLOWED_TRANSITIONS, key=lambda pair: (pair[0].value, pair[1].value)))
def test_allowed_transition_is_accepted(current, target):
    assert can_transition(current, target) is True
    assert apply_transition(current, target) == target


@pytest.mark.parametrize("current,target", sorted(FORBIDDEN_PAIRS, key=lambda pair: (pair[0].value, pair[1].value)))
def test_forbidden_transition_is_rejected(current, target):
    assert can_transition(current, target) is False
    with pytest.raises(IllegalTransitionError):
        apply_transition(current, target)


def test_terminal_state_cannot_return_to_non_terminal():
    for terminal in TERMINAL_STATES:
        for state in ALL_STATES - TERMINAL_STATES:
            assert can_transition(terminal, state) is False
            with pytest.raises(IllegalTransitionError):
                apply_transition(terminal, state)


def test_cancelling_is_one_way():
    assert can_transition(TaskState.CANCELLING, TaskState.RUNNING) is False
    assert can_transition(TaskState.CANCELLING, TaskState.PAUSED) is False


def test_cannot_skip_plan_approval_from_draft_to_running():
    assert can_transition(TaskState.DRAFT, TaskState.RUNNING) is False
    with pytest.raises(IllegalTransitionError):
        apply_transition(TaskState.DRAFT, TaskState.RUNNING)


def test_planning_cannot_go_directly_to_completed():
    assert can_transition(TaskState.PLANNING, TaskState.COMPLETED) is False
    with pytest.raises(IllegalTransitionError):
        apply_transition(TaskState.PLANNING, TaskState.COMPLETED)


