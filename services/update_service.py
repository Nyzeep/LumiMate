from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.request
import zipfile
from pathlib import Path

from config import PROJECT_ROOT
from core.events import EventHook
from core.integrity import DEFAULT_CORE_FILES


class UpdateService:
    def __init__(self, manifest_url: str = "", project_root: Path | None = None):
        self.manifest_url = manifest_url.strip()
        self.project_root = project_root or PROJECT_ROOT
        self.progress = EventHook()
        self.finished = EventHook()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self.is_alive():
            return
        self._thread = threading.Thread(target=self.check_and_apply, name="LumiUpdateService", daemon=True)
        self._thread.start()

    def is_alive(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def request_stop(self) -> None:
        self._stop_event.set()

    def join(self, timeout: float | None = None) -> None:
        if self._thread:
            self._thread.join(timeout=timeout)

    def check_and_apply(self) -> None:
        if not self.manifest_url:
            self.finished.emit(False, "Update source is not configured.")
            return

        backup_dir: Path | None = None
        try:
            self.progress.emit("Downloading update manifest...")
            manifest = self._download_json(self.manifest_url)
            package_url = str(manifest.get("package_url") or "").strip()
            if not package_url:
                self.finished.emit(False, "Update manifest has no package_url.")
                return

            with tempfile.TemporaryDirectory(prefix="lumimate_update_") as temp_name:
                temp_dir = Path(temp_name)
                package_path = temp_dir / "package.zip"
                extract_dir = temp_dir / "extract"
                backup_dir = temp_dir / "backup"

                self.progress.emit("Downloading update package...")
                self._download_file(package_url, package_path)
                expected_sha = str(manifest.get("sha256") or "").strip().lower()
                if expected_sha and self._sha256(package_path) != expected_sha:
                    self.finished.emit(False, "Update package checksum mismatch.")
                    return

                self.progress.emit("Extracting update package...")
                with zipfile.ZipFile(package_path) as archive:
                    archive.extractall(extract_dir)

                self.progress.emit("Backing up current files...")
                self._backup_files(backup_dir)

                self.progress.emit("Applying update...")
                self._copy_tree(extract_dir, self.project_root)

                self.progress.emit("Restarting LumiMate...")
                subprocess.Popen([sys.executable, str(self.project_root / "launcher.py")], cwd=str(self.project_root))
                self.finished.emit(True, "Update applied. LumiMate is restarting.")
        except Exception as exc:
            if backup_dir and backup_dir.exists():
                try:
                    self._copy_tree(backup_dir, self.project_root)
                except Exception as rollback_exc:
                    self.finished.emit(False, f"Update failed: {exc}; rollback failed: {rollback_exc}")
                    return
            self.finished.emit(False, f"Update failed: {exc}")

    def _download_json(self, url: str) -> dict:
        with urllib.request.urlopen(url, timeout=30) as response:
            payload = response.read().decode("utf-8")
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError("Manifest must be a JSON object.")
        return data

    def _download_file(self, url: str, path: Path) -> None:
        with urllib.request.urlopen(url, timeout=120) as response, path.open("wb") as handle:
            shutil.copyfileobj(response, handle)

    def _backup_files(self, backup_dir: Path) -> None:
        for relative in DEFAULT_CORE_FILES:
            source = self.project_root / relative
            if not source.exists():
                continue
            target = backup_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def _copy_tree(self, source: Path, target: Path) -> None:
        for item in source.rglob("*"):
            relative = item.relative_to(source)
            destination = target / relative
            if item.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
