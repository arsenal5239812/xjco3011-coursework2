"""HTML parsing for quotes.toscrape.com pages."""

from __future__ import annotations

from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from search_engine.models import ParsedPage


def parse_quote_page(html: str, url: str, base_url: str) -> ParsedPage:
    """Extract searchable text and internal links from a quote page."""

    soup = BeautifulSoup(html, "html.parser")
    title = _page_title(soup)
    text = _extract_searchable_text(soup)
    links = tuple(_extract_internal_links(soup, url, base_url))
    return ParsedPage(url=url, title=title, text=text, links=links)


def _page_title(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    if soup.title:
        title_text = soup.title.get_text(" ", strip=True)
        if title_text:
            return title_text
    heading = soup.find(["h1", "h2"])
    return heading.get_text(" ", strip=True) if heading else "Untitled page"


def _extract_searchable_text(soup: BeautifulSoup) -> str:
    parts: list[str] = []
    for quote in soup.select(".quote"):
        quote_text = quote.select_one(".text")
        author = quote.select_one(".author")
        tags = quote.select(".tags .tag")
        if quote_text:
            parts.append(quote_text.get_text(" ", strip=True))
        if author:
            parts.append(author.get_text(" ", strip=True))
        parts.extend(tag.get_text(" ", strip=True) for tag in tags)

    if parts:
        return " ".join(parts)

    body = soup.body or soup
    return body.get_text(" ", strip=True)


def _extract_internal_links(soup: BeautifulSoup, current_url: str, base_url: str) -> list[str]:
    base_netloc = urlparse(base_url).netloc
    links: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        absolute = urldefrag(urljoin(current_url, anchor["href"]))[0]
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"} or parsed.netloc != base_netloc:
            continue
        if absolute not in seen:
            links.append(absolute)
            seen.add(absolute)
    return links
