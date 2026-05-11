from io import StringIO
from pathlib import Path

from search_engine.cli import SearchShell, build_parser, run
from search_engine.config import POLITENESS_WINDOW_SECONDS
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
    assert "hello world hello" in output


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


def test_shell_help_blank_unknown_and_exit():
    stdout = StringIO()
    shell = SearchShell(stdin=StringIO("help\n\nbogus\nexit\n"), stdout=stdout)

    assert shell.run() == 0

    output = stdout.getvalue()
    assert "Available commands" in output
    assert "Unknown command: bogus" in output
    assert "Goodbye." in output


def test_shell_uses_loaded_index_for_print_and_find(tmp_path):
    index = build_index(
        [ParsedPage(url="https://example.test/1", title="One", text="hello world hello", links=())],
        base_url="https://example.test/",
    )
    path = tmp_path / "index.json"
    save_index(index, path)
    stdout = StringIO()
    shell = SearchShell(index_path=path, stdin=StringIO("load\nprint world\nfind hello\nexit\n"), stdout=stdout)

    assert shell.run() == 0

    output = stdout.getvalue()
    assert "Loaded index version" in output
    assert "Term: world" in output
    assert "hello world hello" in output


def test_shell_preserves_phrase_query_quotes():
    index = build_index(
        [
            ParsedPage(url="https://example.test/1", title="One", text="brave new world", links=()),
            ParsedPage(url="https://example.test/2", title="Two", text="brave old new", links=()),
        ],
        base_url="https://example.test/",
    )
    stdout = StringIO()
    shell = SearchShell(stdin=StringIO('find "brave new"\nexit\n'), stdout=stdout)
    shell.index = index

    assert shell.run() == 0

    output = stdout.getvalue()
    assert "doc=1" in output
    assert "doc=2" not in output


def test_shell_print_and_find_before_load_show_friendly_message():
    stdout = StringIO()
    shell = SearchShell(stdin=StringIO("find world\nprint world\nexit\n"), stdout=stdout)

    assert shell.run() == 0

    assert stdout.getvalue().count("No index loaded. Run build or load first.") == 2


def test_shell_build_keeps_index_in_memory_and_uses_politeness(monkeypatch, tmp_path):
    created = {}

    class FakeCrawler:
        def __init__(self, base_url, politeness_window_seconds):
            created["base_url"] = base_url
            created["politeness_window_seconds"] = politeness_window_seconds

        def crawl_all(self, max_pages=None, progress_callback=None):
            created["max_pages"] = max_pages
            page = ParsedPage(url="https://example.test/1", title="One", text="fresh world", links=())
            if progress_callback:
                progress_callback(1, page.url)
            return [page]

    monkeypatch.setattr("search_engine.cli.PoliteCrawler", FakeCrawler)
    stdout = StringIO()
    shell = SearchShell(
        index_path=tmp_path / "index.json",
        base_url="https://example.test/",
        stdin=StringIO("build --max-pages 1\nfind world\nexit\n"),
        stdout=stdout,
    )

    assert shell.run() == 0

    output = stdout.getvalue()
    assert created == {
        "base_url": "https://example.test/",
        "politeness_window_seconds": POLITENESS_WINDOW_SECONDS,
        "max_pages": 1,
    }
    assert "Crawled 1: https://example.test/1" in output
    assert "Built index with 1 documents" in output
    assert "fresh world" in output


def test_argparse_build_passes_optional_page_limit_and_keeps_default_unlimited(monkeypatch, tmp_path, capsys):
    calls = []

    class FakeCrawler:
        def __init__(self, base_url, politeness_window_seconds):
            calls.append({"base_url": base_url, "politeness_window_seconds": politeness_window_seconds})

        def crawl_all(self, max_pages=None, progress_callback=None):
            calls[-1]["max_pages"] = max_pages
            page = ParsedPage(url="https://example.test/1", title="One", text="world", links=())
            if progress_callback:
                progress_callback(1, page.url)
            return [page]

    monkeypatch.setattr("search_engine.cli.PoliteCrawler", FakeCrawler)

    assert run(["build", "--index", str(tmp_path / "limited.json"), "--base-url", "https://example.test/", "--max-pages", "2"]) == 0
    assert run(["build", "--index", str(tmp_path / "full.json"), "--base-url", "https://example.test/"]) == 0

    output = capsys.readouterr().out
    assert "Crawled 1:" in output
    assert calls[0]["max_pages"] == 2
    assert calls[1]["max_pages"] is None
    assert all(call["politeness_window_seconds"] == POLITENESS_WINDOW_SECONDS for call in calls)
