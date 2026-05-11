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
