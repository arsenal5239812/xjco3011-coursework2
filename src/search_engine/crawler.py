"""Polite site crawler for quotes.toscrape.com."""

from __future__ import annotations

import logging
import time
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from urllib.parse import urlparse, urldefrag, urljoin

import requests

from search_engine.config import (
    BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
    POLITENESS_WINDOW_SECONDS,
    USER_AGENT,
)
from search_engine.models import CrawledPage
from search_engine.parser import parse_quote_page

LOGGER = logging.getLogger(__name__)


class PoliteCrawler:
    """Breadth-first crawler that avoids revisits and spaces requests."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        politeness_window_seconds: float = POLITENESS_WINDOW_SECONDS,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        session: requests.Session | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.base_url = _canonical_url(base_url)
        self.politeness_window_seconds = politeness_window_seconds
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._sleep = sleeper
        self._clock = clock
        self._last_request_at: float | None = None

    def crawl(self, start_url: str | None = None, max_pages: int | None = None) -> Iterator[CrawledPage]:
        """Crawl internal pages from start_url using breadth-first order."""

        first_url = _canonical_url(urljoin(self.base_url, start_url or self.base_url))
        queue: deque[str] = deque([first_url])
        seen: set[str] = set()

        while queue and (max_pages is None or len(seen) < max_pages):
            url = queue.popleft()
            if url in seen:
                continue
            seen.add(url)

            html = self._fetch(url)
            if html is None:
                continue

            page = CrawledPage(url=url, html=html)
            yield page

            parsed = parse_quote_page(html, url, self.base_url)
            for link in sorted(parsed.links, key=_crawl_priority):
                canonical = _canonical_url(link)
                if canonical not in seen and canonical not in queue:
                    queue.append(canonical)

    def crawl_all(self, start_url: str | None = None, max_pages: int | None = None) -> list[CrawledPage]:
        """Return crawled pages as a list."""

        return list(self.crawl(start_url=start_url, max_pages=max_pages))

    def _fetch(self, url: str) -> str | None:
        self._wait_if_needed()
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            self._last_request_at = self._clock()
            response.raise_for_status()
        except requests.RequestException as exc:
            LOGGER.warning("Failed to fetch %s: %s", url, exc)
            return None

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and content_type:
            LOGGER.info("Skipping non-HTML response %s (%s)", url, content_type)
            return None
        return response.text

    def _wait_if_needed(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = self._clock() - self._last_request_at
        wait_for = self.politeness_window_seconds - elapsed
        if wait_for > 0:
            self._sleep(wait_for)


def crawl_pages(
    base_url: str = BASE_URL,
    max_pages: int | None = None,
    session: requests.Session | None = None,
) -> Iterable[CrawledPage]:
    """Convenience wrapper for crawling the target site."""

    return PoliteCrawler(base_url=base_url, session=session).crawl(max_pages=max_pages)


def _canonical_url(url: str) -> str:
    clean = urldefrag(url)[0]
    return clean.rstrip("/") + "/"


def _crawl_priority(url: str) -> tuple[int, str]:
    path = urlparse(url).path
    if path == "/" or path.startswith("/page/"):
        return (0, url)
    return (1, url)
