from search_engine.tokenizer import normalize_term, positions_by_term, terms_from_query, tokenize


def test_tokenize_lowercases_and_tracks_positions():
    tokens = tokenize("Hello, WORLD! Hello again.")

    assert [(token.term, token.position) for token in tokens] == [
        ("hello", 0),
        ("world", 1),
        ("hello", 2),
        ("again", 3),
    ]


def test_tokenize_handles_empty_text():
    assert tokenize("") == []


def test_normalize_term_removes_punctuation():
    assert normalize_term("World!") == "world"
    assert normalize_term("...") == ""


def test_terms_from_query_returns_unique_ordered_terms():
    assert terms_from_query("Life life WORLD") == ["life", "world"]


def test_positions_by_term_groups_positions():
    grouped = positions_by_term(tokenize("a b a"))

    assert grouped == {"a": [0, 2], "b": [1]}


def test_tokenize_apostrophes_numbers_and_hyphens_explicitly():
    tokens = tokenize("Don't stop 24/7 high-quality work.")

    assert [token.term for token in tokens] == ["don't", "stop", "24", "7", "high", "quality", "work"]


def test_normalize_term_handles_noisy_inputs():
    assert normalize_term("...Don't!!!") == "don't"
    assert normalize_term("42,") == "42"
    assert normalize_term("high-quality") == "high"
