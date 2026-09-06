"""Shared classification for the restricted Task Agent shell commands."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Literal


ALLOWED_CHECK_COMMANDS: tuple[str, ...] = (
    "pytest",
    "npm run build",
    "runtime/server.py --check",
)

ALLOWED_GIT_COMMANDS: tuple[str, ...] = (
    "git status",
    "git diff",
    "git log",
    "git rev-parse",
    "git branch",
)

BashCommandKind = Literal["check", "git"]

_SHELL_CONTROL_MARKERS: tuple[str, ...] = (
    "&&",
    "||",
    ";",
    "|",
    "&",
    "`",
    "$",
    "<",
    ">",
    "\r",
    "\n",
    "\x00",
)
_PYTHON_EXECUTABLE = re.compile(
    r'^(?:"?(?:[a-z]:)?[^";&|<>`$\r\n]*[\\/])?python(?:\.exe)?"?(?=\s|$)',
    re.IGNORECASE,
)
_READ_ONLY_GIT_PREFIXES: tuple[str, ...] = (
    "git status",
    "git diff",
    "git log",
    "git rev-parse",
)
_GIT_DIFF_WRITE_OPTIONS = frozenset(
    {"--output", "--ext-diff", "--textconv", "--no-index"}
)
_READ_ONLY_BRANCH_OPTIONS = frozenset(
    {
        "--show-current",
        "--list",
        "-a",
        "--all",
        "-r",
        "--remotes",
        "-vv",
        "--verbose",
    }
)


@lru_cache(maxsize=256)
def classify_bash_command(command: str | None) -> BashCommandKind | None:
    """Classify one shell command, rejecting command composition and writes.

    纯函数：一次工具决策会经白名单、classify_action、category_for_action
    多次到达这里，缓存避免对同一命令串重复解析。
    """
    normalized = str(command or "").strip().lower()
    if not normalized or any(marker in normalized for marker in _SHELL_CONTROL_MARKERS):
        return None
    if _is_check_command(normalized):
        return "check"
    if _is_read_only_git_command(normalized):
        return "git"
    return None


def _is_check_command(command: str) -> bool:
    if _has_word_prefix(command, "pytest"):
        return True
    if _matches_python_command(command, "-m pytest"):
        return True
    if _has_word_prefix(command, "npm run build"):
        return True
    return _matches_python_command(command, "runtime/server.py --check")


def _matches_python_command(command: str, suffix: str) -> bool:
    match = _PYTHON_EXECUTABLE.match(command)
    if match is None:
        return False
    return _has_word_prefix(command[match.end() :].strip(), suffix)


def _is_read_only_git_command(command: str) -> bool:
    if command == "git branch":
        return True
    if _has_word_prefix(command, "git branch"):
        args = command[len("git branch") :].strip().split()
        return bool(args) and all(arg in _READ_ONLY_BRANCH_OPTIONS for arg in args)

    for prefix in _READ_ONLY_GIT_PREFIXES:
        if not _has_word_prefix(command, prefix):
            continue
        if prefix != "git diff":
            return True
        args = command[len(prefix) :].strip().split()
        return not any(
            arg in _GIT_DIFF_WRITE_OPTIONS
            or any(arg.startswith(f"{option}=") for option in _GIT_DIFF_WRITE_OPTIONS)
            or arg.startswith("-o")
            for arg in args
        )
    return False


def _has_word_prefix(command: str, prefix: str) -> bool:
    return command == prefix or command.startswith(f"{prefix} ")
