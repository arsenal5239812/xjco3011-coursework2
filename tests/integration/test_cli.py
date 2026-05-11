from pathlib import Path

from search_engine.cli import build_parser, run
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
    output = capsys.readouterr().out
    assert "doc=1" in output
    assert "Matched terms: hello" in output


def test_cli_reports_no_results(tmp_path, capsys):
    index = build_index([ParsedPage(url="https://example.test/1", title="One", text="hello", links=())])
    path = tmp_path / "index.json"
    save_index(index, path)

    assert run(["--index", str(path), "find", "missing"]) == 0

    assert "No results found" in capsys.readouterr().out


def test_cli_reports_empty_find_query_cleanly(tmp_path, capsys):
    index = build_index([ParsedPage(url="https://example.test/1", title="One", text="hello", links=())])
    path = tmp_path / "index.json"
    save_index(index, path)

    assert run(["--index", str(path), "find"]) == 0

    assert "No query supplied" in capsys.readouterr().out


def test_cli_accepts_index_option_before_or_after_subcommand(tmp_path):
    path = tmp_path / "index.json"

    before = build_parser().parse_args(["--index", str(path), "load"])
    after = build_parser().parse_args(["load", "--index", str(path)])
    build_after = build_parser().parse_args(["build", "--index", str(path), "--max-pages", "1"])

    assert before.index == path
    assert after.index == path
    assert build_after.index == path
    assert isinstance(build_after.index, Path)
