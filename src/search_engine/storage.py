"""Save and load index files."""

from __future__ import annotations

import json
from pathlib import Path


class IndexStorageError(RuntimeError):
    """Raised when an index cannot be loaded or saved cleanly."""


def save_index(index: dict, path: str | Path) -> Path:
    """Write an index to a JSON file."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    except OSError as exc:
        raise IndexStorageError(f"Could not save index to {target}: {exc}") from exc
    return target


def load_index(path: str | Path) -> dict:
    """Read and validate an index JSON file."""

    source = Path(path)
    if not source.exists():
        raise IndexStorageError(f"Index file does not exist: {source}")
    try:
        index = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IndexStorageError(f"Index file is not valid JSON: {source}") from exc
    except OSError as exc:
        raise IndexStorageError(f"Could not read index from {source}: {exc}") from exc

    _validate_index(index, source)
    return index


def _validate_index(index: object, source: Path) -> None:
    if not isinstance(index, dict):
        raise IndexStorageError(f"Index file has invalid root object: {source}")
    for key in ("metadata", "documents", "terms"):
        if key not in index or not isinstance(index[key], dict):
            raise IndexStorageError(f"Index file is missing '{key}' object: {source}")
