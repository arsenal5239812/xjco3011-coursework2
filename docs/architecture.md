# Architecture

The project is organized as a small pipeline:

1. `crawler.py` fetches pages from the configured base URL. It uses breadth-first traversal, tracks visited URLs, follows only internal links, and enforces the six second politeness window between HTTP requests.
2. `parser.py` extracts quote text, authors, tags, page title, and internal links from each HTML page.
3. `tokenizer.py` normalizes text to lowercase terms and records zero-based token positions.
4. `indexer.py` builds the positional inverted index. Each term stores document frequency and per-document postings with term frequency and positions.
5. `storage.py` saves and loads the JSON index, reporting missing and corrupted files clearly.
6. `search.py` handles term lookup, ranked search, phrase queries, and simple boolean queries.
7. `ranking.py` scores matching documents with a TF-IDF style formula.
8. `cli.py` wires the modules into the required `build`, `load`, `print`, and `find` commands.

The modules deliberately exchange plain dataclasses and JSON-serializable dictionaries. This keeps the data flow easy to inspect and makes the saved index format match the in-memory structure closely.

## Design Choices

- The crawler takes injectable `session`, `sleeper`, and `clock` dependencies so tests can avoid live network calls and real waiting.
- The parser prefers quote-specific selectors. If a malformed or unexpected page has no quote cards, it falls back to body text.
- Search is case-insensitive because every indexed term and query term uses the same tokenizer.
- Multi-term `find` queries use AND semantics by default, which gives precise results for a small quote corpus.
- Phrase search uses token positions in postings rather than scanning original HTML again.
