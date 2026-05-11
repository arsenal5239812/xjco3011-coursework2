"""Command-line interface for building and querying the search index."""

from __future__ import annotations

import argparse
import logging
import shlex
from pathlib import Path
from typing import TextIO

from search_engine.config import BASE_URL, DEFAULT_INDEX_PATH, POLITENESS_WINDOW_SECONDS
from search_engine.crawler import PoliteCrawler
from search_engine.indexer import build_index
from search_engine.search import find, format_term_lookup
from search_engine.storage import IndexStorageError, load_index, save_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mini search engine for quotes.toscrape.com")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH, help="Path to index JSON file")
    parser.add_argument("--verbose", action="store_true", help="Enable informational logging")
    subparsers = parser.add_subparsers(dest="command")

    build = subparsers.add_parser("build", help="Crawl the site and save a new index")
    _add_subcommand_index_option(build)
    build.add_argument("--base-url", default=BASE_URL)
    build.add_argument("--max-pages", type=int, default=None)

    load = subparsers.add_parser("load", help="Validate and summarize an existing index")
    _add_subcommand_index_option(load)

    print_cmd = subparsers.add_parser("print", help="Print postings for a term")
    _add_subcommand_index_option(print_cmd)
    print_cmd.add_argument("term")

    find_cmd = subparsers.add_parser("find", help="Find ranked pages for a query")
    _add_subcommand_index_option(find_cmd)
    find_cmd.add_argument("query", nargs="*", help="Search query. Omit it to demonstrate empty-query handling.")
    find_cmd.add_argument("--limit", type=int, default=10)

    shell = subparsers.add_parser("shell", help="Start an interactive search shell")
    _add_subcommand_index_option(shell)
    shell.add_argument("--base-url", default=BASE_URL)

    return parser


def _add_subcommand_index_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--index",
        type=Path,
        default=argparse.SUPPRESS,
        help="Path to index JSON file",
    )


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        if args.command is None:
            return SearchShell(index_path=args.index).run()
        if args.command == "build":
            return _run_build(args)
        if args.command == "load":
            return _run_load(args)
        if args.command == "print":
            return _run_print(args)
        if args.command == "find":
            return _run_find(args)
        if args.command == "shell":
            return SearchShell(index_path=args.index, base_url=args.base_url).run()
    except IndexStorageError as exc:
        parser.exit(2, f"{exc}\n")
    return 1


def _run_build(args: argparse.Namespace) -> int:
    _build_and_save_index(
        index_path=args.index,
        base_url=args.base_url,
        max_pages=args.max_pages,
        show_progress=True,
    )
    return 0


def _build_and_save_index(
    index_path: Path,
    base_url: str = BASE_URL,
    max_pages: int | None = None,
    show_progress: bool = True,
    output: Callable[[str], None] | None = None,
) -> dict:
    crawler = PoliteCrawler(
        base_url=base_url,
        politeness_window_seconds=POLITENESS_WINDOW_SECONDS,
    )
    writer = output or print
    progress = (lambda count, url: writer(f"Crawled {count}: {url}")) if show_progress else None
    pages = crawler.crawl_all(max_pages=max_pages, progress_callback=progress)
    index = build_index(
        pages,
        base_url=base_url,
        politeness_window_seconds=POLITENESS_WINDOW_SECONDS,
    )
    save_index(index, index_path)
    writer(
        f"Built index with {index['metadata']['document_count']} documents and "
        f"{index['metadata']['unique_term_count']} unique terms at {index_path}"
    )
    return index


def _print_progress(count: int, url: str) -> None:
    print(f"Crawled {count}: {url}")


def _run_load(args: argparse.Namespace) -> int:
    index = load_index(args.index)
    metadata = index["metadata"]
    print(
        f"Loaded index version {metadata.get('version')} with "
        f"{metadata.get('document_count')} documents and {metadata.get('unique_term_count')} unique terms."
    )
    return 0


def _run_print(args: argparse.Namespace) -> int:
    index = load_index(args.index)
    print(format_term_lookup(index, args.term))
    return 0


def _run_find(args: argparse.Namespace) -> int:
    index = load_index(args.index)
    query = " ".join(args.query)
    if not query.strip():
        print("No query supplied. Please enter one or more search terms.")
        return 0

    results = find(index, query, limit=args.limit)
    if not results:
        print(f"No results found for '{query}'.")
        return 0

    for rank, result in enumerate(results, start=1):
        terms = ", ".join(result.matched_terms)
        print(f"{rank}. score={result.score:.4f} doc={result.doc_id} terms={terms}")
        print(f"   {result.title}")
        print(f"   {result.url}")
        if result.snippet:
            print(f"   {result.snippet}")
    return 0


class SearchShell:
    """Interactive shell that keeps a loaded index in memory."""

    def __init__(
        self,
        index_path: Path = DEFAULT_INDEX_PATH,
        base_url: str = BASE_URL,
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
    ) -> None:
        self.index_path = Path(index_path)
        self.base_url = base_url
        self.stdin = stdin
        self.stdout = stdout
        self.index: dict | None = None

    def run(self) -> int:
        self._write("Mini search shell. Type help for commands, exit to quit.")
        while True:
            try:
                line = self._input("search> ")
            except EOFError:
                self._write("")
                return 0

            should_continue = self.handle_line(line)
            if not should_continue:
                return 0

    def handle_line(self, line: str) -> bool:
        line = line.strip()
        if not line:
            return True

        try:
            parts = shlex.split(line)
        except ValueError as exc:
            self._write(f"Could not parse command: {exc}")
            return True

        command, args = parts[0].lower(), parts[1:]
        raw_args = line[len(parts[0]) :].strip()
        try:
            if command == "help":
                self._print_help()
            elif command in {"exit", "quit"}:
                self._write("Goodbye.")
                return False
            elif command == "build":
                self._shell_build(args)
            elif command == "load":
                self._shell_load()
            elif command == "print":
                self._shell_print(args)
            elif command == "find":
                self._shell_find(raw_args)
            else:
                self._write(f"Unknown command: {command}. Type help for available commands.")
        except IndexStorageError as exc:
            self._write(str(exc))
        return True

    def _shell_build(self, args: list[str]) -> None:
        parser = argparse.ArgumentParser(prog="build", add_help=False)
        parser.add_argument("--max-pages", type=int, default=None)
        parser.add_argument("--base-url", default=self.base_url)
        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            self._write("Usage: build [--max-pages N] [--base-url URL]")
            return

        self.index = _build_and_save_index(
            index_path=self.index_path,
            base_url=parsed.base_url,
            max_pages=parsed.max_pages,
            show_progress=True,
            output=self._write,
        )
        self.base_url = parsed.base_url

    def _shell_load(self) -> None:
        self.index = load_index(self.index_path)
        metadata = self.index["metadata"]
        self._write(
            f"Loaded index version {metadata.get('version')} with "
            f"{metadata.get('document_count')} documents and {metadata.get('unique_term_count')} unique terms."
        )

    def _shell_print(self, args: list[str]) -> None:
        if not self._has_index():
            return
        if not args:
            self._write("Usage: print <term>")
            return
        self._write(format_term_lookup(self.index, args[0]))

    def _shell_find(self, query: str) -> None:
        if not self._has_index():
            return
        if not query.strip():
            self._write("No query supplied. Please enter one or more search terms.")
            return
        results = find(self.index, query)
        if not results:
            self._write(f"No results found for '{query}'.")
            return
        for rank, result in enumerate(results, start=1):
            terms = ", ".join(result.matched_terms)
            self._write(f"{rank}. score={result.score:.4f} doc={result.doc_id} terms={terms}")
            self._write(f"   {result.title}")
            self._write(f"   {result.url}")
            if result.snippet:
                self._write(f"   {result.snippet}")

    def _has_index(self) -> bool:
        if self.index is not None:
            return True
        self._write("No index loaded. Run build or load first.")
        return False

    def _print_help(self) -> None:
        self._write("Available commands: build, load, print <term>, find <query>, help, exit")

    def _input(self, prompt: str) -> str:
        if self.stdin is None:
            return input(prompt)
        self._write(prompt, end="")
        line = self.stdin.readline()
        if line == "":
            raise EOFError
        return line

    def _write(self, text: str, end: str = "\n") -> None:
        print(text, end=end, file=self.stdout)
