$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "src"
python -m search_engine.main build --index data/index.json
