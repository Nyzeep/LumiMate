import os
import sys
from pathlib import Path

import pytest

import launcher


def test_resolve_tool_prefers_windows_cmd_suffix(monkeypatch):
    if os.name != "nt":
        pytest.skip("Windows-only candidate ordering")
    attempts = []
    monkeypatch.setattr(
        launcher.shutil,
        "which",
        lambda candidate: attempts.append(candidate)
        or ("C:\\fake\\npm.cmd" if candidate == "npm.cmd" else None),
    )
    assert launcher._resolve_tool("npm") == "C:\\fake\\npm.cmd"
    assert attempts[0] == "npm.cmd"


def test_resolve_tool_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(launcher.shutil, "which", lambda _: None)
    assert launcher._resolve_tool("definitely-not-a-tool") is None


def test_check_project_files_raises_on_missing_files(monkeypatch, tmp_path):
    monkeypatch.setattr(launcher, "PROJECT_ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="Missing required LumiMate files"):
        launcher._check_project_files()


def test_launcher_check_smoke(monkeypatch):
    monkeypatch.setattr(launcher, "_resolve_python", lambda: Path(sys.executable))
    monkeypatch.setattr(launcher, "_install_requirements", lambda python_exe: None)
    assert launcher.main(["--check"]) == 0
