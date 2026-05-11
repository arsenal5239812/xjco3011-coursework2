import requests

from search_engine.crawler import PoliteCrawler


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code
        self.headers = {"content-type": "text/html"}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


class FakeSession:
    def __init__(self, pages):
        self.pages = pages
        self.headers = {}
        self.requested = []

    def get(self, url, timeout):
        self.requested.append((url, timeout))
        return FakeResponse(self.pages[url])


def test_crawler_walks_internal_links_and_sleeps_between_requests(fixture_html):
    pages = {
        "https://quotes.toscrape.com/": fixture_html("page_1.html"),
        "https://quotes.toscrape.com/page/2/": fixture_html("page_2.html"),
        "https://quotes.toscrape.com/tag/change/page/1/": "<html><body>change</body></html>",
        "https://quotes.toscrape.com/tag/world/page/1/": "<html><body>world</body></html>",
        "https://quotes.toscrape.com/tag/choices/page/1/": "<html><body>choices</body></html>",
    }
    clock_values = iter([0.0, 1.0, 7.0, 8.0, 14.0, 15.0, 21.0, 22.0, 28.0])
    sleeps = []
    crawler = PoliteCrawler(
        session=FakeSession(pages),
        sleeper=sleeps.append,
        clock=lambda: next(clock_values),
    )

    crawled = crawler.crawl_all(max_pages=2)

    assert [page.url for page in crawled] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert sleeps == [5.0]


def test_crawler_default_scope_ignores_non_listing_pages(fixture_html):
    pages = {
        "https://quotes.toscrape.com/": fixture_html("page_1.html").replace(
            "</body>",
            '<a href="/author/Albert-Einstein/">Author</a><a href="/login">Login</a></body>',
        ),
        "https://quotes.toscrape.com/page/2/": fixture_html("page_2.html"),
    }
    session = FakeSession(pages)
    crawler = PoliteCrawler(
        session=session,
        sleeper=lambda seconds: None,
        clock=lambda: 10.0,
    )

    crawled = crawler.crawl_all(max_pages=10)

    assert [page.url for page in crawled] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    requested_urls = [url for url, _ in session.requested]
    assert "https://quotes.toscrape.com/tag/world/page/1/" not in requested_urls
    assert "https://quotes.toscrape.com/author/Albert-Einstein/" not in requested_urls
    assert "https://quotes.toscrape.com/login/" not in requested_urls


def test_crawler_progress_callback_reports_successful_pages(fixture_html):
    crawler = PoliteCrawler(
        session=FakeSession({"https://quotes.toscrape.com/": fixture_html("page_1.html")}),
        sleeper=lambda seconds: None,
        clock=lambda: 10.0,
    )
    progress = []

    crawler.crawl_all(max_pages=1, progress_callback=lambda count, url: progress.append((count, url)))

    assert progress == [(1, "https://quotes.toscrape.com/")]


def test_crawler_skips_failed_requests():
    class ErrorSession(FakeSession):
        def get(self, url, timeout):
            raise requests.Timeout("slow")

    crawler = PoliteCrawler(session=ErrorSession({}))

    assert crawler.crawl_all(max_pages=1) == []
