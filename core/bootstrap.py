from __future__ import annotations

import importlib.metadata
import os
import subprocess
import sys
import venv
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class BootstrapResult:
    ok: bool
    restarted: bool = False
    message: str = ""
    phase: str = "ready"


class AppBootstrap:
    @staticmethod
    def preferred_venv(project_root: Path) -> Path:
        candidates = [project_root / ".venv", project_root.parent / ".venv"]
        for venv_root in candidates:
            python_path = (
                venv_root / "Scripts" / "python.exe"
                if os.name == "nt"
                else venv_root / "bin" / "python"
            )
            if python_path.exists():
                return venv_root
        return project_root / ".venv"

    @staticmethod
    def preferred_python(project_root: Path) -> Path:
        venv_root = AppBootstrap.preferred_venv(project_root)
        if os.name == "nt":
            return venv_root / "Scripts" / "python.exe"
        return venv_root / "bin" / "python"

    @staticmethod
    def ensure_environment(project_root: Path) -> BootstrapResult:
        if os.environ.get("LUMIMATE_SKIP_BOOTSTRAP") == "1":
            return BootstrapResult(True, message="Bootstrap skipped by environment.", phase="ready")

        preferred = AppBootstrap.preferred_python(project_root)
        requirements = project_root / "requirements.txt"
        current_python = Path(sys.executable)
        try:
            if not AppBootstrap._missing_requirements(requirements, current_python):
                return AppBootstrap._ensure_frontend(project_root)
        except Exception:
            pass

        try:
            created_venv = False
            if not preferred.exists():
                venv.EnvBuilder(with_pip=True, clear=False).create(str(AppBootstrap.preferred_venv(project_root)))
                created_venv = True
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to create virtual environment: {exc}", phase="failed")

        try:
            target_python = preferred if preferred.exists() else Path(sys.executable)
            force_install = created_venv
            install_result = AppBootstrap._ensure_requirements(project_root, target_python, force_install=force_install)
            if not install_result.ok:
                return install_result
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to validate dependencies: {exc}", phase="failed")

        try:
            current = Path(sys.executable).resolve()
            if preferred.exists() and current != preferred.resolve():
                os.execv(str(preferred), [str(preferred), str(project_root / "main.py"), *sys.argv[1:]])
                return BootstrapResult(True, restarted=True, message="Restarted with project venv.", phase="ready")
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to restart with project venv: {exc}", phase="failed")

        return AppBootstrap._ensure_frontend(project_root)

    @staticmethod
    def _ensure_requirements(project_root: Path, python_exe: Path, force_install: bool = False) -> BootstrapResult:
        requirements = project_root / "requirements.txt"
        if not requirements.exists():
            return BootstrapResult(True, message="No requirements.txt found.", phase="ready")

        try:
            missing = AppBootstrap._missing_requirements(requirements, python_exe)
        except Exception:
            missing = ["requirements"]

        if not force_install and not missing:
            return BootstrapResult(True, message="Dependencies ready.", phase="ready")

        try:
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "-r", str(requirements)],
                cwd=str(project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return BootstrapResult(True, message="Dependencies installed.", phase="ready")
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to install dependencies: {exc}", phase="failed")

    @staticmethod
    def _missing_requirements(requirements: Path, python_exe: Path) -> list[str]:
        if not requirements.exists():
            return []

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
            names.append(name)

        if not names:
            return []

        current_python = Path(sys.executable).resolve()
        if python_exe.exists() and python_exe.resolve() != current_python:
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

    @staticmethod
    def _ensure_frontend(project_root: Path) -> BootstrapResult:
        frontend_entry = project_root / "ui" / "web" / "dist" / "index.html"
        if not frontend_entry.exists():
            return BootstrapResult(
                False,
                message=(
                    f"Failed to find built Web frontend: {frontend_entry}\n"
                    "Run: cd ui\\web && npm install && npm run build"
                ),
                phase="failed",
            )
        return BootstrapResult(True, message="Environment ready.", phase="ready")
