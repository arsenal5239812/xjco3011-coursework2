"""Default configuration for the mini search engine."""

from __future__ import annotations

from pathlib import Path

BASE_URL = "https://quotes.toscrape.com/"
DEFAULT_TIMEOUT_SECONDS = 10
POLITENESS_WINDOW_SECONDS = 6.0
INDEX_FORMAT_VERSION = "1.0"
DEFAULT_INDEX_PATH = Path("data/index.json")
USER_AGENT = "xjco3011-coursework2-mini-search/0.1"
