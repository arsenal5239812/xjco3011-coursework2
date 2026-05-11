"""Dataclasses used across crawling, indexing, and searching."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrawledPage:
    """A fetched HTML page before parsing and indexing."""

    url: str
    html: str


@dataclass(frozen=True)
class ParsedPage:
    """Relevant text and links extracted from a crawled page."""

    url: str
    title: str
    text: str
    links: tuple[str, ...] = ()


@dataclass(frozen=True)
class Token:
    """A normalized token and its zero-based position in a document."""

    term: str
    position: int


@dataclass
class Posting:
    """Index entry for one term inside one document."""

    frequency: int = 0
    positions: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class Document:
    """Metadata for a document in the index."""

    doc_id: str
    url: str
    title: str
    word_count: int


@dataclass(frozen=True)
class SearchResult:
    """Ranked search hit."""

    doc_id: str
    url: str
    title: str
    score: float
    matched_terms: tuple[str, ...]
    snippet: str = ""
