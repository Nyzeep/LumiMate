from pathlib import Path

from services.model_catalog import (
    MODEL_DOWNLOAD_CATALOG,
    directory_size_bytes,
    discover_model_directories,
)


def test_catalog_covers_three_kinds_with_required_fields():
    assert set(MODEL_DOWNLOAD_CATALOG) == {"asr", "llm", "tts"}
    for kind, entries in MODEL_DOWNLOAD_CATALOG.items():
        for entry in entries:
            assert entry["id"]
            assert entry["title"]
            assert isinstance(entry["providers"], dict)


def test_discover_model_directories_returns_leaf_dirs_with_files(tmp_path):
    root = tmp_path / "models"
    (root / "asr" / "ASR_model").mkdir(parents=True)
    (root / "asr" / "ASR_model" / "config.json").write_text("{}", encoding="utf-8")
    (root / "asr" / "empty").mkdir()
    (root / "asr" / "nested" / "leaf").mkdir(parents=True)
    (root / "asr" / "nested" / "leaf" / "model.bin").write_bytes(b"x")

    found = discover_model_directories(root)
    assert str(root / "asr" / "ASR_model") in found
    assert str(root / "asr" / "nested" / "leaf") in found


def test_discover_model_directories_returns_empty_for_missing_root(tmp_path):
    assert discover_model_directories(tmp_path / "missing") == []


def test_directory_size_bytes_sums_file_sizes(tmp_path):
    folder = tmp_path / "storage"
    folder.mkdir()
    (folder / "a.bin").write_bytes(b"12345")
    (folder / "b.bin").write_bytes(b"123")
    assert directory_size_bytes(folder) == 8


def test_directory_size_bytes_returns_zero_for_missing_root(tmp_path):
    assert directory_size_bytes(tmp_path / "missing") == 0
