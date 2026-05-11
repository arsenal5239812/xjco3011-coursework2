from search_engine.indexer import build_index
from search_engine.models import ParsedPage
from search_engine.ranking import rank_documents, score_document


def test_ranking_prefers_higher_term_density():
    index = build_index(
        [
            ParsedPage(url="https://example.test/1", title="One", text="life life life", links=()),
            ParsedPage(url="https://example.test/2", title="Two", text="life world world world", links=()),
        ],
        base_url="https://example.test/",
    )

    ranked = rank_documents(index, {"1", "2"}, ["life"])

    assert ranked[0][0] == "1"
    assert score_document(index, "1", ["life"]) > score_document(index, "2", ["life"])
