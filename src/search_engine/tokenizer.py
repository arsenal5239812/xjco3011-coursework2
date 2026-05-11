"""Text normalization and positional tokenization."""

from __future__ import annotations

import re
from collections.abc import Iterable

from search_engine.models import Token

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)


def normalize_term(term: str) -> str:
    """Normalize a single term for case-insensitive lookup."""

    matches = TOKEN_RE.findall(term.lower())
    return matches[0] if matches else ""


def tokenize(text: str) -> list[Token]:
    """Split text into lowercase tokens with zero-based positions."""

    tokens: list[Token] = []
    for position, match in enumerate(TOKEN_RE.finditer(text.lower())):
        tokens.append(Token(term=match.group(0), position=position))
    return tokens


def terms_from_query(query: str) -> list[str]:
    """Normalize query text into unique ordered terms."""

    seen: set[str] = set()
    terms: list[str] = []
    for token in tokenize(query):
        if token.term not in seen:
            terms.append(token.term)
            seen.add(token.term)
    return terms


def positions_by_term(tokens: Iterable[Token]) -> dict[str, list[int]]:
    """Group token positions by term."""

    positions: dict[str, list[int]] = {}
    for token in tokens:
        positions.setdefault(token.term, []).append(token.position)
    return positions
