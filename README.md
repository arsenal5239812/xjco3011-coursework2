# XJCO3011 Coursework 2: Mini Search Engine

A small, modular Python search engine for [quotes.toscrape.com](https://quotes.toscrape.com/). It politely crawls quote pages, builds a positional inverted index, saves the compiled index as JSON, and supports command-line lookup and ranked retrieval.

## Features

- Polite breadth-first crawler with a six second request spacing rule.
- HTML parser for quote text, authors, tags, page titles, and internal links.
- Case-insensitive positional tokenization.
- Positional inverted index with frequencies and document metadata.
- JSON persistence with validation on load.
- `build`, `load`, `print`, and `find` CLI commands.
- TF-IDF style ranked retrieval for single and multi-term queries.
- Phrase queries with quoted text, for example `"brave new"`.
- Simple boolean queries using `AND`, `OR`, and `NOT`.
- Unit and integration tests with deterministic fixtures.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

## Usage

Build an index from the live site:

```powershell
python -m search_engine.main build --index data/index.json
```

Limit the crawl during development:

```powershell
python -m search_engine.main build --index data/index.json --max-pages 5
```

Validate and summarize a saved index:

```powershell
python -m search_engine.main --index data/index.json load
```

Print postings for one term:

```powershell
python -m search_engine.main --index data/index.json print world
```

Find ranked results:

```powershell
python -m search_engine.main --index data/index.json find Albert Einstein
python -m search_engine.main --index data/index.json find '"there are only"'
python -m search_engine.main --index data/index.json find life OR world
```

## Commands

`build` crawls the target site and writes a new index.

`load` reads the index file and prints a short summary.

`print <term>` shows document frequency, term frequency, positions, and URLs for a single term.

`find <query>` searches the index and prints ranked results. Plain multi-term queries use AND semantics by default.

## Testing

```powershell
pytest
pytest --cov
```

The crawler tests use fake sessions and fake sleep functions, so they do not depend on live network access and do not wait six seconds.

## Project Layout

```text
src/search_engine/
  crawler.py    polite crawling and URL discovery
  parser.py     quote page text and link extraction
  tokenizer.py  normalization and positional tokens
  indexer.py    positional inverted index construction
  ranking.py    TF-IDF style scoring
  search.py     lookup, find, phrase, and boolean search
  storage.py    JSON persistence and validation
  cli.py        command-line interface
```

Supporting documentation is in `docs/`, tests are in `tests/`, and helper scripts are in `scripts/`.

## Known Limitations

This is intentionally a focused coursework search engine rather than a general web crawler. It only follows internal links for the configured site, stores a compact JSON index in memory, and implements simple boolean parsing without parentheses or operator precedence beyond left-to-right evaluation.
