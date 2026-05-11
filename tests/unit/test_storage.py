import pytest

from search_engine.indexer import build_index
from search_engine.models import ParsedPage
from search_engine.storage import IndexStorageError, load_index, save_index


def test_storage_round_trips_index(tmp_path):
    index = build_index([ParsedPage(url="https://example.test", title="Test", text="hello world", links=())])
    path = tmp_path / "index.json"

    save_index(index, path)

    assert load_index(path) == index


def test_load_index_reports_missing_file(tmp_path):
    with pytest.raises(IndexStorageError, match="does not exist"):
        load_index(tmp_path / "missing.json")


def test_load_index_reports_corrupt_file(tmp_path):
    path = tmp_path / "index.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(IndexStorageError, match="not valid JSON"):
        load_index(path)
