"""TF-IDF style ranking for search results."""

from __future__ import annotations

import math


def score_document(index: dict, doc_id: str, query_terms: list[str]) -> float:
    """Return a TF-IDF score for one document and query."""

    documents = index.get("documents", {})
    terms = index.get("terms", {})
    document_count = max(1, int(index.get("metadata", {}).get("document_count", len(documents)) or 1))
    word_count = max(1, int(documents.get(doc_id, {}).get("word_count", 1) or 1))
    score = 0.0

    for term in query_terms:
        term_entry = terms.get(term)
        if not term_entry:
            continue
        posting = term_entry.get("postings", {}).get(doc_id)
        if not posting:
            continue
        tf = posting["frequency"] / word_count
        idf = math.log((1 + document_count) / (1 + term_entry["document_frequency"])) + 1
        score += tf * idf
    return score


def rank_documents(index: dict, doc_ids: set[str], query_terms: list[str]) -> list[tuple[str, float]]:
    """Rank document ids by score, then by stable numeric document id."""

    scored = [(doc_id, score_document(index, doc_id, query_terms)) for doc_id in doc_ids]
    return sorted(scored, key=lambda item: (-item[1], int(item[0]) if item[0].isdigit() else item[0]))
