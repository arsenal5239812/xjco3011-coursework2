"""Command-line interface for building and querying the search index."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from search_engine.config import BASE_URL, DEFAULT_INDEX_PATH, POLITENESS_WINDOW_SECONDS
from search_engine.crawler import PoliteCrawler
from search_engine.indexer import build_index
from search_engine.search import find, format_term_lookup
from search_engine.storage import IndexStorageError, load_index, save_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mini search engine for quotes.toscrape.com")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH, help="Path to index JSON file")
    parser.add_argument("--verbose", action="store_true", help="Enable informational logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Crawl the site and save a new index")
    build.add_argument("--base-url", default=BASE_URL)
    build.add_argument("--max-pages", type=int, default=None)

    subparsers.add_parser("load", help="Validate and summarize an existing index")

    print_cmd = subparsers.add_parser("print", help="Print postings for a term")
    print_cmd.add_argument("term")

    find_cmd = subparsers.add_parser("find", help="Find ranked pages for a query")
    find_cmd.add_argument("query", nargs="+")
    find_cmd.add_argument("--limit", type=int, default=10)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        if args.command == "build":
            return _run_build(args)
        if args.command == "load":
            return _run_load(args)
        if args.command == "print":
            return _run_print(args)
        if args.command == "find":
            return _run_find(args)
    except IndexStorageError as exc:
        parser.exit(2, f"{exc}\n")
    return 1


def _run_build(args: argparse.Namespace) -> int:
    crawler = PoliteCrawler(
        base_url=args.base_url,
        politeness_window_seconds=POLITENESS_WINDOW_SECONDS,
    )
    pages = crawler.crawl_all(max_pages=args.max_pages)
    index = build_index(
        pages,
        base_url=args.base_url,
        politeness_window_seconds=POLITENESS_WINDOW_SECONDS,
    )
    save_index(index, args.index)
    print(
        f"Built index with {index['metadata']['document_count']} documents and "
        f"{index['metadata']['unique_term_count']} unique terms at {args.index}"
    )
    return 0


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
    results = find(index, query, limit=args.limit)
    if not results:
        print(f"No results found for '{query}'.")
        return 0

    for rank, result in enumerate(results, start=1):
        terms = ", ".join(result.matched_terms)
        print(f"{rank}. score={result.score:.4f} doc={result.doc_id} terms={terms}")
        print(f"   {result.title}")
        print(f"   {result.url}")
    return 0
