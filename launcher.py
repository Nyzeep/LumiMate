from __future__ import annotations

import os
import importlib.metadata
import subprocess
import sys
import venv
from pathlib import Path


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


PROJECT_ROOT = _project_root()
QUIET = "--verbose-bootstrap" not in sys.argv
BOOTSTRAP_MARKER = "LUMIMATE_BOOTSTRAPPED"


def _venv_python() -> Path:
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def _is_usable_python(python_exe: Path) -> bool:
    return python_exe.exists() and not _missing_requirements(PROJECT_ROOT / "requirements.txt", python_exe)


def _current_python_is_usable() -> bool:
    if os.environ.get(BOOTSTRAP_MARKER) == "1":
        return True
    requirements = PROJECT_ROOT / "requirements.txt"
    return not requirements.exists() or not _missing_requirements(requirements, Path(sys.executable))


def _resolve_python() -> Path:
    if _current_python_is_usable():
        return Path(sys.executable)

    project_venv = _venv_python()
    if _is_usable_python(project_venv):
        return project_venv

    return _ensure_venv()


def _ensure_venv() -> Path:
    python_exe = _venv_python()
    if python_exe.exists():
        return python_exe

    _notice("LumiMate: creating local Python environment...")
    venv.EnvBuilder(with_pip=True, clear=False).create(str(PROJECT_ROOT / ".venv"))
    if not python_exe.exists():
        raise RuntimeError("Virtual environment was created, but its Python executable was not found.")
    return python_exe


def _install_requirements(python_exe: Path) -> None:
    requirements = PROJECT_ROOT / "requirements.txt"
    if not requirements.exists():
        return
    missing = _missing_requirements(requirements, python_exe)
    if not missing:
        return
    _notice("LumiMate: preparing dependencies. This may take a while on first launch...")
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-r", str(requirements)],
        cwd=str(PROJECT_ROOT),
        stdout=None if not QUIET else subprocess.DEVNULL,
        stderr=None if not QUIET else subprocess.DEVNULL,
        check=True,
    )


def _missing_requirements(requirements: Path, python_exe: Path) -> list[str]:
    names: list[str] = []
    for raw_line in requirements.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        package = line.split(";", 1)[0].strip()
        name = package
        for marker in ("==", ">=", "<=", "~=", "!=", ">", "<"):
            if marker in name:
                name = name.split(marker, 1)[0].strip()
                break
        if name:
            names.append(name)

    if not names:
        return []

    if python_exe.resolve() != Path(sys.executable).resolve():
        code = (
            "import importlib.metadata, sys\n"
            "missing=[]\n"
            "for name in sys.argv[1:]:\n"
            "    try:\n"
            "        importlib.metadata.version(name)\n"
            "    except importlib.metadata.PackageNotFoundError:\n"
            "        missing.append(name)\n"
            "print('\\n'.join(missing))\n"
        )
        result = subprocess.run(
            [str(python_exe), "-c", code, *names],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return names
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    missing: list[str] = []
    for name in names:
        try:
            importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            try:
                importlib.metadata.version(name.replace("_", "-"))
            except importlib.metadata.PackageNotFoundError:
                missing.append(name)
    return missing


def _check_frontend() -> None:
    frontend = PROJECT_ROOT / "ui" / "web" / "dist" / "index.html"
    if frontend.exists():
        return
    raise RuntimeError(
        "The Web frontend has not been built yet. Run `cd ui\\web && npm install && npm run build` before launching LumiMate."
    )


def _notice(message: str) -> None:
    if not QUIET:
        print(message)


def main() -> int:
    try:
        python_exe = _resolve_python()
        _install_requirements(python_exe)
        _check_frontend()
        os.environ["LUMIMATE_SKIP_BOOTSTRAP"] = "1"
        os.environ[BOOTSTRAP_MARKER] = "1"
        args = [arg for arg in sys.argv[1:] if arg != "--verbose-bootstrap"]
        command = [str(python_exe), str(PROJECT_ROOT / "main.py"), *args]
        return subprocess.call(command, cwd=str(PROJECT_ROOT))
    except Exception as exc:
        print(f"LumiMate launcher failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
