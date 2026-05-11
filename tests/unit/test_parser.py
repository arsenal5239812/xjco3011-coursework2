from search_engine.parser import parse_quote_page


def test_parser_extracts_quote_text_authors_tags_and_internal_links(fixture_html):
    parsed = parse_quote_page(
        fixture_html("page_1.html"),
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/",
    )

    assert parsed.title == "Quotes to Scrape"
    assert "Albert Einstein" in parsed.text
    assert "choices" in parsed.text
    assert "https://quotes.toscrape.com/page/2/" in parsed.links
    assert "https://quotes.toscrape.com/tag/world/page/1/" in parsed.links


def test_parser_filters_external_links(fixture_html):
    parsed = parse_quote_page(
        fixture_html("page_2.html"),
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/",
    )

    assert all("quotes.toscrape.com" in link for link in parsed.links)
    assert "https://example.com/outside" not in parsed.links


def test_parser_handles_malformed_html(fixture_html):
    parsed = parse_quote_page(
        fixture_html("malformed.html"),
        "https://quotes.toscrape.com/broken/",
        "https://quotes.toscrape.com/",
    )

    assert "Broken" in parsed.title
    assert "Broken but readable" in parsed.text
