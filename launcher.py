from __future__ import annotations

import argparse
import importlib.metadata
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


PROJECT_ROOT = _project_root()
BOOTSTRAP_MARKER = "LUMIMATE_BOOTSTRAPPED"


def _ensure_rust_path() -> None:
    cargo_bin = Path.home() / ".cargo" / "bin"
    if not cargo_bin.exists():
        return
    cargo_bin_text = str(cargo_bin)
    paths = os.environ.get("PATH", "").split(os.pathsep)
    if not any(Path(item).resolve() == cargo_bin.resolve() for item in paths if item):
        os.environ["PATH"] = cargo_bin_text + os.pathsep + os.environ.get("PATH", "")


def _venv_python() -> Path:
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def _resolve_python() -> Path:
    requirements = PROJECT_ROOT / "requirements.txt"
    if os.environ.get(BOOTSTRAP_MARKER) == "1":
        return Path(sys.executable)
    if not requirements.exists() or not _missing_requirements(requirements, Path(sys.executable)):
        return Path(sys.executable)

    project_venv = _venv_python()
    if project_venv.exists() and not _missing_requirements(requirements, project_venv):
        return project_venv

    return _ensure_venv()


def _ensure_venv() -> Path:
    python_exe = _venv_python()
    if python_exe.exists():
        return python_exe
    print("LumiMate: creating local Python environment...")
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
    print("LumiMate: preparing Python runtime dependencies...")
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-r", str(requirements)],
        cwd=str(PROJECT_ROOT),
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
        if "[" in name:
            name = name.split("[", 1)[0].strip()
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


def _check_project_files() -> None:
    required = [
        PROJECT_ROOT / "runtime" / "server.py",
        PROJECT_ROOT / "ui" / "web" / "src" / "app" / "AppShell.vue",
        PROJECT_ROOT / "ui" / "web" / "src-tauri" / "tauri.conf.json",
        PROJECT_ROOT / "背景图片" / "背景1.png",
        PROJECT_ROOT / "背景图片" / "背景2.png",
        PROJECT_ROOT / "背景图片" / "背景3.png",
        PROJECT_ROOT / "背景图片" / "背景4.png",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Missing required LumiMate files:\n" + "\n".join(missing))


def _run_runtime(python_exe: Path, args: list[str]) -> int:
    os.environ[BOOTSTRAP_MARKER] = "1"
    if python_exe.resolve() == Path(sys.executable).resolve():
        from runtime.server import main as runtime_main

        return runtime_main(args)
    command = [str(python_exe), "-m", "runtime.server", *args]
    return subprocess.call(command, cwd=str(PROJECT_ROOT), env={**os.environ, BOOTSTRAP_MARKER: "1"})


def _run_desktop() -> int:
    _ensure_rust_path()
    frontend = PROJECT_ROOT / "ui" / "web"
    if not (frontend / "src-tauri" / "tauri.conf.json").exists():
        print("LumiMate desktop shell is missing. Run `python launcher.py --api` to start the backend only.")
        return 1

    if not shutil.which("cargo"):
        print(
            "LumiMate now uses Tauri as the desktop shell.\n"
            "Rust/Cargo is not installed, so the native UI cannot be started from `python launcher.py` yet.\n\n"
            "Install Rust from https://rustup.rs, then run:\n"
            "  cd ui\\web\n"
            "  npm run tauri:dev\n\n"
            "Backend-only mode is still available with:\n"
            "  python launcher.py --api"
        )
        return 1

    return subprocess.call(["npm", "run", "tauri:dev"], cwd=str(frontend))


def main(argv: list[str] | None = None) -> int:
    _ensure_rust_path()
    parser = argparse.ArgumentParser(description="LumiMate launcher")
    parser.add_argument("--api", action="store_true", help="Start the Python FastAPI runtime.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    try:
        python_exe = _resolve_python()
        _install_requirements(python_exe)
        _check_project_files()
        if not args.api and not args.check:
            return _run_desktop()
        runtime_args: list[str] = []
        if args.check:
            runtime_args.append("--check")
        if args.api or not args.check:
            runtime_args.extend(["--host", args.host, "--port", str(args.port)])
        result = _run_runtime(python_exe, runtime_args)
        if args.check and result == 0:
            print("LumiMate launcher check passed.")
        return result
    except Exception as exc:
        print(f"LumiMate launcher failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
