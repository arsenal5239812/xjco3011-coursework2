# Testing Strategy

The test suite is split into unit and integration tests.

## Unit Tests

- `test_tokenizer.py` checks lowercase normalization, punctuation handling, apostrophes, numbers, hyphens, empty input, unique query terms, and positions.
- `test_parser.py` checks quote text, author, tag, link extraction, external link filtering, and malformed HTML.
- `test_indexer.py` checks document metadata, previews, frequencies, positions, and metadata counts.
- `test_ranking.py` checks that TF-IDF scoring prefers more relevant documents.
- `test_search.py` checks case-insensitive lookup, AND-style queries, phrase search, boolean search, ranking limits, snippets, and print output.
- `test_search.py` also covers empty queries, missing terms, snippets, and the Boolean `NOT` regression where the right-hand side has no matches.
- `test_storage.py` checks JSON round-tripping and clear failures for missing, corrupt, or structurally invalid files.
- `test_main.py` checks that the module entry point delegates to the CLI runner.

## Integration Tests

- `test_crawler.py` uses a fake HTTP session, fake clock, and fake sleeper. This verifies listing-page traversal, non-listing page filtering, progress callbacks, and the politeness rule without live network access or real delays.
- `test_cli.py` exercises direct CLI commands and the interactive shell, including `help`, `load`, `print`, `find`, phrase-query quote preservation, no-index-loaded output, no-result output, empty-query output, build state, progress output, and both supported `--index` option positions.
- `test_build_load_find.py` builds an index from HTML fixtures, saves it, loads it, and searches it.

## Coverage Target

The practical target is at least 85 percent coverage. The current local suite has 47 tests and 90 percent total coverage. The tests focus on the important behaviours: correctness of the index, reliable persistence, deterministic search results, interactive shell behavior, and polite crawling.
