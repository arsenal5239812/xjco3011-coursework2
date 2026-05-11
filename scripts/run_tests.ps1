$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "src"
pytest --cov
