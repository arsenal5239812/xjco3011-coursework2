from search_engine.indexer import build_index
from search_engine.models import CrawledPage
from search_engine.search import find
from search_engine.storage import load_index, save_index


def test_build_save_load_find_end_to_end(fixture_html, tmp_path):
    pages = [
        CrawledPage(url="https://quotes.toscrape.com/", html=fixture_html("page_1.html")),
        CrawledPage(url="https://quotes.toscrape.com/page/2/", html=fixture_html("page_2.html")),
    ]

    index = build_index(pages, base_url="https://quotes.toscrape.com/")
    path = tmp_path / "index.json"
    save_index(index, path)
    loaded = load_index(path)
    results = find(loaded, "Albert Einstein")

    assert loaded["metadata"]["document_count"] == 2
    assert [result.doc_id for result in results] == ["2", "1"]
