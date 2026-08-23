from services.agent.tools.registry import (
    ALLOWED_CHECK_COMMANDS,
    ALLOWED_TOOL_NAMES,
    is_allowed_tool,
)


def test_whitelisted_tool_names_allowed():
    for tool in ("read", "read_image", "write", "edit", "test", "lint", "typecheck"):
        assert is_allowed_tool(tool) is True


def test_whitelisted_check_commands_allowed_via_bash():
    for command in (
        "python -m pytest tests/test_x.py",
        "pytest",
        "npm run build",
        "python runtime/server.py --check",
    ):
        assert is_allowed_tool("bash", {"command": command}) is True


def test_git_status_commands_allowed_via_bash():
    for command in ("git status", "git diff", "git log --oneline -5", "git rev-parse HEAD"):
        assert is_allowed_tool("bash", {"command": command}) is True


def test_non_whitelisted_tools_denied():
    for tool in ("network", "install", "system_program", "system_settings", "unknown_tool", "delete"):
        assert is_allowed_tool(tool) is False


def test_non_whitelisted_bash_commands_denied():
    for command in (
        "pip install requests",
        "rm -rf .",
        "curl https://example.com",
        "start notepad.exe",
        "npm install left-pad",
    ):
        assert is_allowed_tool("bash", {"command": command}) is False


def test_bash_without_arguments_denied():
    assert is_allowed_tool("bash") is False
    assert is_allowed_tool("bash", {}) is False


def test_whitelist_constants_match_section20():
    assert "pytest" in ALLOWED_CHECK_COMMANDS
    assert "npm run build" in ALLOWED_CHECK_COMMANDS
    assert "runtime/server.py --check" in ALLOWED_CHECK_COMMANDS
    assert "read" in ALLOWED_TOOL_NAMES
    assert "write" in ALLOWED_TOOL_NAMES

