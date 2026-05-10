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


class AppBootstrap:
    @staticmethod
    def preferred_python(project_root: Path) -> Path:
        if os.name == "nt":
            return project_root.parent / ".venv" / "Scripts" / "python.exe"
        return project_root.parent / ".venv" / "bin" / "python"

    @staticmethod
    def ensure_environment(project_root: Path) -> BootstrapResult:
        if os.environ.get("LUMIMATE_SKIP_BOOTSTRAP") == "1":
            return BootstrapResult(True, message="Bootstrap skipped by environment.")

        preferred = AppBootstrap.preferred_python(project_root)
        try:
            created_venv = False
            if not preferred.exists():
                venv.EnvBuilder(with_pip=True, clear=False).create(str(preferred.parents[1] if os.name == "nt" else preferred.parents[1]))
                created_venv = True
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to create virtual environment: {exc}")

        try:
            target_python = preferred if preferred.exists() else Path(sys.executable)
            force_install = created_venv
            install_result = AppBootstrap._ensure_requirements(project_root, target_python, force_install=force_install)
            if not install_result.ok:
                return install_result
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to validate dependencies: {exc}")

        try:
            current = Path(sys.executable).resolve()
            if preferred.exists() and current != preferred.resolve():
                os.execv(str(preferred), [str(preferred), str(project_root / "main.py"), *sys.argv[1:]])
                return BootstrapResult(True, restarted=True)
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to restart with project venv: {exc}")

        return BootstrapResult(True, message="Environment ready.")

    @staticmethod
    def _ensure_requirements(project_root: Path, python_exe: Path, force_install: bool = False) -> BootstrapResult:
        requirements = project_root / "requirements.txt"
        if not requirements.exists():
            return BootstrapResult(True, message="No requirements.txt found.")

        try:
            missing = AppBootstrap._missing_requirements(requirements, python_exe)
        except Exception:
            missing = ["requirements"]

        if not force_install and not missing:
            return BootstrapResult(True, message="Dependencies ready.")

        try:
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "-r", str(requirements)],
                cwd=str(project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return BootstrapResult(True, message="Dependencies installed.")
        except Exception as exc:
            return BootstrapResult(False, message=f"Failed to install dependencies: {exc}")

    @staticmethod
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
                missing.append(name)
        return missing
