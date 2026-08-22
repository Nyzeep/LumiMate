from __future__ import annotations

from pathlib import Path
from typing import Any


MODEL_DOWNLOAD_CATALOG: dict[str, list[dict[str, Any]]] = {
    "asr": [
        {
            "id": "qwen3-asr-flash",
            "title": "Qwen3 ASR Flash",
            "subtitle": "轻量听觉节点，适合作为 Lumi 的默认耳朵。",
            "sizeLabel": "约 5 GB",
            "providers": {
                "modelscope": "Qwen/Qwen3-ASR-Flash",
                "huggingface": "Qwen/Qwen3-ASR-Flash",
            },
        },
        {
            "id": "qwen2-audio-7b",
            "title": "Qwen2 Audio 7B",
            "subtitle": "更完整的音频理解节点，下载和运行成本更高。",
            "sizeLabel": "约 15 GB",
            "providers": {
                "modelscope": "qwen/Qwen2-Audio-7B-Instruct",
                "huggingface": "Qwen/Qwen2-Audio-7B-Instruct",
            },
        },
    ],
    "llm": [
        {
            "id": "qwen2-5-0-5b-instruct",
            "title": "Qwen2.5 0.5B Instruct",
            "subtitle": "小体量思维核心，适合先让 Lumi 轻盈醒来。",
            "sizeLabel": "约 1 GB",
            "providers": {
                "modelscope": "qwen/Qwen2.5-0.5B-Instruct",
                "huggingface": "Qwen/Qwen2.5-0.5B-Instruct",
            },
        },
        {
            "id": "qwen2-5-1-5b-instruct",
            "title": "Qwen2.5 1.5B Instruct",
            "subtitle": "更稳定的本地对话核心，需要更多显存与磁盘空间。",
            "sizeLabel": "约 3 GB",
            "providers": {
                "modelscope": "qwen/Qwen2.5-1.5B-Instruct",
                "huggingface": "Qwen/Qwen2.5-1.5B-Instruct",
            },
        },
    ],
    "tts": [
        {
            "id": "tts-placeholder",
            "title": "声线星系预留",
            "subtitle": "TTS 将在后续版本支持用户自行加载角色声线模型。",
            "sizeLabel": "稍后开放",
            "providers": {},
            "placeholder": True,
        }
    ],
}


def discover_model_directories(root: Path) -> list[str]:
    if not root.exists():
        return []
    if any(root.iterdir()) and any(item.is_file() for item in root.iterdir()):
        return [str(root)]

    candidates: list[str] = []
    for child in sorted(root.iterdir(), key=lambda path: path.name.lower()):
        if not child.is_dir():
            continue
        if any(item.is_file() for item in child.iterdir()):
            candidates.append(str(child))
            continue
        for nested in sorted(child.rglob("*"), key=lambda path: path.name.lower()):
            if nested.is_dir() and any(item.is_file() for item in nested.iterdir()):
                candidates.append(str(nested))
    deduped: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def directory_size_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    total = 0
    for file_path in root.rglob("*"):
        if file_path.is_file():
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
    return total
