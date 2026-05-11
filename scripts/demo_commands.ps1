$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "src"
python -m search_engine.main --index data/index.json load
python -m search_engine.main --index data/index.json print world
python -m search_engine.main --index data/index.json find Albert Einstein
python -m search_engine.main --index data/index.json find '"there are only"'
