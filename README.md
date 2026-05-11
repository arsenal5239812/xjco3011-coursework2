# XJCO3011 Coursework 2: Mini Search Engine

A small, modular Python search engine for [quotes.toscrape.com](https://quotes.toscrape.com/). It politely crawls quote listing pages, builds a positional inverted index, saves the compiled index as JSON, and supports both an interactive shell and direct command-line lookup.

## Features

- Polite breadth-first crawler with a six second request spacing rule.
- Focused crawl scope for quote listing pages (`/` and `/page/N/`).
- HTML parser for quote text, authors, tags, page titles, and internal links.
- Case-insensitive positional tokenization.
- Positional inverted index with frequencies, positions, document metadata, and result previews.
- JSON persistence with validation on load.
- Interactive shell commands for `build`, `load`, `print`, and `find`.
- Direct CLI subcommands for the same workflow.
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

### Interactive shell

The coursework brief describes a shell-style interface. Start it with:

```powershell
python -m search_engine.main shell --index data/index.json
```

Then run commands at the `search>` prompt:

```text
load
print world
find Albert Einstein
find good friends
find "there are only"
find
find definitelynotintheindex
exit
```

Use `build` inside the shell to crawl the live site and write a fresh index:

```text
build
```

For a shorter development run, limit the crawl explicitly:

```text
build --max-pages 3
```

### Direct commands

Build a complete index from the live site:

```powershell
python -m search_engine.main build --index data/index.json
```

Limit the crawl during development:

```powershell
python -m search_engine.main build --index data/index.json --max-pages 5
```

The CLI also accepts global options before the subcommand:

```powershell
python -m search_engine.main --index data/index.json build --max-pages 5
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
python -m search_engine.main --index data/index.json find brave NOT missing
python -m search_engine.main --index data/index.json find
```

If the package is installed with `python -m pip install -e .`, the console script is available too:

```powershell
mini-search --index data/index.json load
mini-search --index data/index.json find Albert Einstein
```

## Commands

`build` crawls the target site and writes a new index. The default build is complete for the focused listing-page scope. Because the crawler respects a six second politeness window, a full build takes longer than the tests.

`load` reads the index file and prints a short summary.

`print <term>` shows document frequency, term frequency, positions, and URLs for a single term.

`find <query>` searches the index and prints ranked results with score, title, URL, matched terms, and a short preview. Plain multi-term queries use AND semantics by default. An empty `find` command prints a friendly message instead of raw parser output.

Query examples:

```text
find Albert Einstein
find good friends
find "there are only"
find life OR world
find brave NOT missing
```

## Testing

```powershell
pytest
pytest --cov
```

The crawler tests use fake sessions and fake sleep functions, so they do not depend on live network access and do not wait six seconds.

Current local verification:

```text
47 passed
90% total coverage
```

For a demo-ready command sequence, see `docs/video_script.md` or run `scripts/demo_commands.ps1`.

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
  cli.py        interactive shell and direct command-line interface
```

Supporting documentation is in `docs/`, tests are in `tests/`, and helper scripts are in `scripts/`.

## Compiled Index

The generated index file is `data/index.json`. It is ignored by Git by default so the file can be submitted separately through Minerva, as required by the coursework. If you want to include it in the repository as well, add it explicitly with `git add -f data/index.json`.

## GenAI Use

This assessment permits GenAI use with declaration and critical evaluation. See `docs/genai_reflection.md` for reflection notes to adapt for the final video demonstration.

## Known Limitations

This is intentionally a focused coursework search engine rather than a general web crawler. It follows quote listing pages for the configured site, stores a compact JSON index in memory, and implements simple boolean parsing without parentheses or full operator precedence. Boolean operators are evaluated by the project's simple left-to-right parser, so complex expressions should be kept small and explicit. The tokenizer keeps common words because phrase search depends on word positions.
