"""Build a positional inverted index from parsed pages."""

from __future__ import annotations

from datetime import datetime, timezone

from search_engine.config import BASE_URL, INDEX_FORMAT_VERSION, POLITENESS_WINDOW_SECONDS
from search_engine.models import CrawledPage, ParsedPage
from search_engine.parser import parse_quote_page
from search_engine.tokenizer import positions_by_term, tokenize


def build_index(
    pages: list[CrawledPage | ParsedPage],
    base_url: str = BASE_URL,
    politeness_window_seconds: float = POLITENESS_WINDOW_SECONDS,
) -> dict:
    """Build the JSON-serializable index structure."""

    documents: dict[str, dict] = {}
    terms: dict[str, dict] = {}
    total_token_count = 0

    for number, page in enumerate(pages, start=1):
        parsed = page if isinstance(page, ParsedPage) else parse_quote_page(page.html, page.url, base_url)
        doc_id = str(number)
        tokens = tokenize(parsed.text)
        grouped_positions = positions_by_term(tokens)
        total_token_count += len(tokens)

        documents[doc_id] = {
            "url": parsed.url,
            "title": parsed.title,
            "word_count": len(tokens),
        }

        for term, positions in grouped_positions.items():
            term_entry = terms.setdefault(term, {"document_frequency": 0, "postings": {}})
            term_entry["postings"][doc_id] = {
                "frequency": len(positions),
                "positions": positions,
            }

    for term_entry in terms.values():
        term_entry["document_frequency"] = len(term_entry["postings"])

    return {
        "metadata": {
            "version": INDEX_FORMAT_VERSION,
            "base_url": base_url,
            "build_time": datetime.now(timezone.utc).isoformat(),
            "politeness_window_seconds": politeness_window_seconds,
            "document_count": len(documents),
            "unique_term_count": len(terms),
            "total_token_count": total_token_count,
        },
        "documents": documents,
        "terms": dict(sorted(terms.items())),
    }


def build_index_from_html_pages(
    pages: list[CrawledPage],
    base_url: str = BASE_URL,
    politeness_window_seconds: float = POLITENESS_WINDOW_SECONDS,
) -> dict:
    """Build an index from crawled HTML pages."""

    return build_index(
        pages,
        base_url=base_url,
        politeness_window_seconds=politeness_window_seconds,
    )
