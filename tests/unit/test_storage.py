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


def test_load_index_reports_invalid_shape(tmp_path):
    path = tmp_path / "index.json"
    path.write_text('{"metadata": {}, "documents": {}}', encoding="utf-8")

    with pytest.raises(IndexStorageError, match="missing 'terms'"):
        load_index(path)


def test_load_index_reports_invalid_root_object(tmp_path):
    path = tmp_path / "index.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(IndexStorageError, match="invalid root object"):
        load_index(path)


def test_load_index_wraps_read_errors(monkeypatch, tmp_path):
    path = tmp_path / "index.json"
    path.write_text("{}", encoding="utf-8")

    def broken_read_text(self, encoding=None):
        raise OSError("disk problem")

    monkeypatch.setattr("pathlib.Path.read_text", broken_read_text)

    with pytest.raises(IndexStorageError, match="Could not read index"):
        load_index(path)


def test_save_index_wraps_write_errors(monkeypatch, tmp_path):
    def broken_write_text(self, text, encoding=None):
        raise OSError("disk problem")

    monkeypatch.setattr("pathlib.Path.write_text", broken_write_text)

    with pytest.raises(IndexStorageError, match="Could not save index"):
        save_index({"metadata": {}, "documents": {}, "terms": {}}, tmp_path / "index.json")
