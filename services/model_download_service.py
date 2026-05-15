from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QThread, Signal


@dataclass(slots=True)
class ModelDownloadRequest:
    kind: str
    provider: str
    model_id: str
    display_name: str
    target_root: Path

    @property
    def target_dir(self) -> Path:
        safe_name = _safe_model_name(self.display_name or self.model_id)
        return self.target_root / safe_name


def _safe_model_name(value: str) -> str:
    name = value.replace("\\", "/").rstrip("/").split("/")[-1].strip()
    cleaned = "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in name)
    return cleaned.strip("._") or "model"


class ModelDownloadService(QThread):
    state_changed = Signal(str, str)
    progress_changed = Signal(int, str)
    log_added = Signal(str)
    finished_with_result = Signal(bool, str, str, str)

    def __init__(self, request: ModelDownloadRequest, parent=None):
        super().__init__(parent)
        self.request = request
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True
        self.requestInterruption()

    def run(self) -> None:
        try:
            self._emit_state("scanning", "正在确认模型星轨坐标...")
            self._emit_progress(4, "正在准备下载目录")
            self.request.target_root.mkdir(parents=True, exist_ok=True)

            if self._cancel_requested:
                self._cancelled()
                return

            self._emit_state("downloading", "正在连接模型星系...")
            self._emit_progress(12, "下载任务已经开始")
            downloaded_path = self._download()

            if self._cancel_requested:
                self._cancelled()
                return

            self._emit_state("organizing", "正在整理本地模型目录...")
            self._emit_progress(86, "正在归档模型资源")
            target_dir = self._organize(downloaded_path)

            if self._cancel_requested:
                self._cancelled()
                return

            self._emit_progress(100, "模型节点已经就位")
            self._emit_state("complete", "模型节点已经进入本地星图。")
            self.finished_with_result.emit(True, self.request.kind, str(target_dir), "模型下载完成。")
        except Exception as exc:
            message = f"模型下载没有完成：{exc}"
            self._emit_state("failed", "模型下载没有完成，请切换来源或稍后重试。")
            self.log_added.emit(message)
            self.finished_with_result.emit(False, self.request.kind, "", message)

    def _download(self) -> Path:
        provider = self.request.provider.lower().strip()
        if provider == "modelscope":
            return self._download_from_modelscope()
        if provider in {"huggingface", "hf"}:
            return self._download_from_huggingface()
        raise ValueError("不支持的模型来源。")

    def _download_from_modelscope(self) -> Path:
        try:
            from modelscope import snapshot_download
        except Exception as exc:
            raise RuntimeError("缺少 modelscope 依赖，请重新运行启动器安装依赖。") from exc

        self.log_added.emit("正在通过魔搭社区下载模型。")
        local_path = snapshot_download(
            self.request.model_id,
            cache_dir=str(self.request.target_root),
        )
        return Path(local_path)

    def _download_from_huggingface(self) -> Path:
        try:
            from huggingface_hub import snapshot_download
        except Exception as exc:
            raise RuntimeError("缺少 huggingface_hub 依赖，请重新运行启动器安装依赖。") from exc

        self.log_added.emit("正在通过 Hugging Face 下载模型。")
        target_dir = self.request.target_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        try:
            local_path = snapshot_download(
                repo_id=self.request.model_id,
                local_dir=str(target_dir),
                local_dir_use_symlinks=False,
            )
        except TypeError:
            local_path = snapshot_download(
                repo_id=self.request.model_id,
                local_dir=str(target_dir),
            )
        return Path(local_path)

    def _organize(self, downloaded_path: Path) -> Path:
        target_dir = self.request.target_dir
        try:
            downloaded = downloaded_path.resolve()
        except OSError:
            downloaded = downloaded_path
        try:
            target = target_dir.resolve()
        except OSError:
            target = target_dir

        if downloaded == target:
            return target_dir

        if target_dir.exists() and any(target_dir.iterdir()):
            return target_dir

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if downloaded_path.exists() and downloaded_path.is_dir():
            if target_dir.exists():
                shutil.rmtree(target_dir)
            try:
                shutil.move(str(downloaded_path), str(target_dir))
            except OSError:
                target_dir.mkdir(parents=True, exist_ok=True)
                for item in downloaded_path.iterdir():
                    destination = target_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, destination, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, destination)
        return target_dir

    def _emit_state(self, state: str, message: str) -> None:
        self.state_changed.emit(state, message)
        self.log_added.emit(message)

    def _emit_progress(self, progress: int, message: str) -> None:
        self.progress_changed.emit(max(0, min(100, progress)), message)

    def _cancelled(self) -> None:
        self._emit_state("cancelled", "模型下载已取消。")
        self.finished_with_result.emit(False, self.request.kind, "", "模型下载已取消。")
