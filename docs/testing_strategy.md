# Testing Strategy

The test suite is split into unit and integration tests.

## Unit Tests

- `test_tokenizer.py` checks lowercase normalization, punctuation handling, empty input, unique query terms, and positions.
- `test_parser.py` checks quote text, author, tag, link extraction, external link filtering, and malformed HTML.
- `test_indexer.py` checks document metadata, frequencies, positions, and metadata counts.
- `test_ranking.py` checks that TF-IDF scoring prefers more relevant documents.
- `test_search.py` checks case-insensitive lookup, AND-style queries, phrase search, boolean search, and print output.
- `test_storage.py` checks JSON round-tripping and clear failures for missing or corrupt files.

## Integration Tests

- `test_crawler.py` uses a fake HTTP session, fake clock, and fake sleeper. This verifies internal link traversal and the politeness rule without live network access or real delays.
- `test_cli.py` exercises `load`, `print`, and `find` through the command runner.
- `test_build_load_find.py` builds an index from HTML fixtures, saves it, loads it, and searches it.

## Coverage Target

The practical target is at least 85 percent coverage. The tests focus on the important behaviours: correctness of the index, reliable persistence, deterministic search results, and polite crawling.
