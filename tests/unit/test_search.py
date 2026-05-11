from search_engine.indexer import build_index
from search_engine.models import ParsedPage
from search_engine.search import find, format_term_lookup, lookup_term


def sample_index():
    return build_index(
        [
            ParsedPage(url="https://example.test/1", title="One", text="brave new world", links=()),
            ParsedPage(url="https://example.test/2", title="Two", text="brave old life", links=()),
            ParsedPage(url="https://example.test/3", title="Three", text="quiet world life", links=()),
        ],
        base_url="https://example.test/",
    )


def test_lookup_term_is_case_insensitive():
    entry = lookup_term(sample_index(), "WORLD!")

    assert entry["document_frequency"] == 2


def test_find_defaults_to_and_query():
    results = find(sample_index(), "brave world")

    assert [result.doc_id for result in results] == ["1"]


def test_find_supports_phrase_query():
    results = find(sample_index(), '"brave new"')

    assert [result.doc_id for result in results] == ["1"]


def test_find_supports_boolean_or_and_not():
    assert {result.doc_id for result in find(sample_index(), "new OR old")} == {"1", "2"}
    assert [result.doc_id for result in find(sample_index(), "brave NOT old")] == ["1"]


def test_format_term_lookup_lists_postings():
    output = format_term_lookup(sample_index(), "world")

    assert "Document frequency: 2" in output
    assert "doc 1" in output
    assert "positions=" in output
