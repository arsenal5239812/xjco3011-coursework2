from search_engine.cli import run
from search_engine.indexer import build_index
from search_engine.models import ParsedPage
from search_engine.storage import save_index


def test_cli_load_print_and_find(tmp_path, capsys):
    index = build_index(
        [ParsedPage(url="https://example.test/1", title="One", text="hello world hello", links=())],
        base_url="https://example.test/",
    )
    path = tmp_path / "index.json"
    save_index(index, path)

    assert run(["--index", str(path), "load"]) == 0
    assert "Loaded index version" in capsys.readouterr().out

    assert run(["--index", str(path), "print", "HELLO"]) == 0
    assert "frequency=2" in capsys.readouterr().out

    assert run(["--index", str(path), "find", "hello"]) == 0
    assert "doc=1" in capsys.readouterr().out


def test_cli_reports_no_results(tmp_path, capsys):
    index = build_index([ParsedPage(url="https://example.test/1", title="One", text="hello", links=())])
    path = tmp_path / "index.json"
    save_index(index, path)

    assert run(["--index", str(path), "find", "missing"]) == 0

    assert "No results found" in capsys.readouterr().out
