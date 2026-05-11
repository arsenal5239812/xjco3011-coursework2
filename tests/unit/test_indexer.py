from search_engine.indexer import build_index
from search_engine.models import ParsedPage


def test_build_index_stores_documents_terms_frequencies_and_positions():
    pages = [
        ParsedPage(url="https://example.test/1", title="One", text="Life is life", links=()),
        ParsedPage(url="https://example.test/2", title="Two", text="World life", links=()),
    ]

    index = build_index(pages, base_url="https://example.test/")

    assert index["metadata"]["document_count"] == 2
    assert index["metadata"]["unique_term_count"] == 3
    assert index["metadata"]["total_token_count"] == 5
    assert index["documents"]["1"]["word_count"] == 3
    assert index["terms"]["life"]["document_frequency"] == 2
    assert index["terms"]["life"]["postings"]["1"] == {"frequency": 2, "positions": [0, 2]}
    assert index["terms"]["world"]["postings"]["2"] == {"frequency": 1, "positions": [0]}
