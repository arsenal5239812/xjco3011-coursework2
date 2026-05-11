# Demo Script

This command sequence is intended for a short assessment recording. Run it from the repository root after installing the development dependencies.

```powershell
$env:PYTHONPATH = "src"
python -m search_engine.main build --index data/index.json --max-pages 3
python -m search_engine.main --index data/index.json load
python -m search_engine.main --index data/index.json print world
python -m search_engine.main --index data/index.json find Albert Einstein
python -m search_engine.main --index data/index.json find '"there are only"'
python -m search_engine.main --index data/index.json find
python -m search_engine.main --index data/index.json find definitelynotintheindex
pytest
git log --oneline --decorate -5
```

The sequence demonstrates index building, loading, term lookup, ranked search, phrase search, empty query handling, no-result handling, tests, and version history.
