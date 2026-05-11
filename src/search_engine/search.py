"""Search operations over the compiled index."""

from __future__ import annotations

import re

from search_engine.models import SearchResult
from search_engine.ranking import rank_documents
from search_engine.tokenizer import normalize_term, tokenize

BOOLEAN_RE = re.compile(r"\s+(AND|OR|NOT)\s+", re.IGNORECASE)
PHRASE_RE = re.compile(r'"([^"]+)"')


def lookup_term(index: dict, raw_term: str) -> dict | None:
    """Return the term entry for a single normalized term."""

    term = normalize_term(raw_term)
    if not term:
        return None
    return index.get("terms", {}).get(term)


def find(index: dict, query: str, limit: int = 10) -> list[SearchResult]:
    """Find documents for a query, supporting terms, phrases, and simple boolean operators."""

    query = query.strip()
    if not query:
        return []

    if _is_phrase_query(query):
        doc_ids, terms = _phrase_doc_ids(index, PHRASE_RE.fullmatch(query).group(1))
    elif BOOLEAN_RE.search(query):
        doc_ids, terms = _boolean_doc_ids(index, query)
    else:
        terms = [token.term for token in tokenize(query)]
        doc_ids = _and_doc_ids(index, terms)

    ranked = rank_documents(index, doc_ids, terms)
    return [_to_result(index, doc_id, score, terms) for doc_id, score in ranked[:limit]]


def format_term_lookup(index: dict, raw_term: str) -> str:
    """Human-friendly print output for one term."""

    term = normalize_term(raw_term)
    if not term:
        return "No valid term supplied."
    entry = lookup_term(index, term)
    if not entry:
        return f"No postings found for '{term}'."

    lines = [f"Term: {term}", f"Document frequency: {entry['document_frequency']}"]
    for doc_id, posting in sorted(entry["postings"].items(), key=lambda item: int(item[0])):
        doc = index["documents"][doc_id]
        lines.append(
            f"- doc {doc_id}: frequency={posting['frequency']}, "
            f"positions={posting['positions']}, url={doc['url']}"
        )
    return "\n".join(lines)


def _is_phrase_query(query: str) -> bool:
    return bool(PHRASE_RE.fullmatch(query))


def _and_doc_ids(index: dict, terms: list[str]) -> set[str]:
    normalized = [term for term in terms if term]
    if not normalized:
        return set()
    postings = [set(index.get("terms", {}).get(term, {}).get("postings", {})) for term in normalized]
    if not postings:
        return set()
    return set.intersection(*postings)


def _or_doc_ids(index: dict, terms: list[str]) -> set[str]:
    doc_ids: set[str] = set()
    for term in terms:
        doc_ids.update(index.get("terms", {}).get(term, {}).get("postings", {}))
    return doc_ids


def _boolean_doc_ids(index: dict, query: str) -> tuple[set[str], list[str]]:
    parts = BOOLEAN_RE.split(query)
    terms = [token.term for token in tokenize(query) if token.term not in {"and", "or", "not"}]
    if not parts:
        return set(), terms

    current = _docs_for_query_part(index, parts[0])
    index_pos = 1
    while index_pos < len(parts):
        operator = parts[index_pos].upper()
        right = _docs_for_query_part(index, parts[index_pos + 1])
        if operator == "AND":
            current &= right
        elif operator == "OR":
            current |= right
        elif operator == "NOT":
            current -= right
        index_pos += 2
    return current, terms


def _docs_for_query_part(index: dict, text: str) -> set[str]:
    terms = [token.term for token in tokenize(text)]
    return _and_doc_ids(index, terms)


def _phrase_doc_ids(index: dict, phrase: str) -> tuple[set[str], list[str]]:
    terms = [token.term for token in tokenize(phrase)]
    if not terms:
        return set(), []

    candidates = _and_doc_ids(index, terms)
    matches: set[str] = set()
    postings_by_term = [index["terms"][term]["postings"] for term in terms]
    for doc_id in candidates:
        first_positions = postings_by_term[0][doc_id]["positions"]
        other_position_sets = [set(postings[doc_id]["positions"]) for postings in postings_by_term[1:]]
        for start in first_positions:
            if all(start + offset + 1 in positions for offset, positions in enumerate(other_position_sets)):
                matches.add(doc_id)
                break
    return matches, terms


def _to_result(index: dict, doc_id: str, score: float, terms: list[str]) -> SearchResult:
    doc = index["documents"][doc_id]
    matched_terms = tuple(term for term in terms if doc_id in index.get("terms", {}).get(term, {}).get("postings", {}))
    return SearchResult(
        doc_id=doc_id,
        url=doc["url"],
        title=doc["title"],
        score=score,
        matched_terms=matched_terms,
        snippet=_make_snippet(doc, matched_terms),
    )


def _make_snippet(doc: dict, matched_terms: tuple[str, ...]) -> str:
    word_count = doc.get("word_count", 0)
    terms = ", ".join(matched_terms) if matched_terms else "none"
    return f"Matched terms: {terms}; indexed words: {word_count}."
