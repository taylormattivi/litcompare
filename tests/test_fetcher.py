import json

import pytest
import requests

from litcompare import fetcher


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.encoding = None

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


BOOK_METADATA = {
    "id": 999,
    "title": "Sample Book",
    "authors": [{"name": "Sample Author"}],
    "formats": {
        "text/plain; charset=utf-8": "https://www.gutenberg.org/ebooks/999.txt.utf-8",
        "application/zip": "https://www.gutenberg.org/ebooks/999.zip",
    },
}

RAW_TEXT = (
    "preamble\n"
    "*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE BOOK ***\n"
    "The actual book content goes here.\n"
    "*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE BOOK ***\n"
    "footer\n"
)


def test_strip_boilerplate_extracts_body_text():
    result = fetcher._strip_boilerplate(RAW_TEXT)
    assert result == "The actual book content goes here."


def test_strip_boilerplate_returns_original_when_no_markers():
    text = "just some plain text with no markers"
    assert fetcher._strip_boilerplate(text) == text


def test_get_plain_text_url_skips_zip():
    url = fetcher._get_plain_text_url(BOOK_METADATA)
    assert url == "https://www.gutenberg.org/ebooks/999.txt.utf-8"


def test_get_plain_text_url_returns_none_when_absent():
    book = {"formats": {"application/zip": "https://example.com/book.zip"}}
    assert fetcher._get_plain_text_url(book) is None


def test_fetch_downloads_and_caches(tmp_path, monkeypatch):
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        calls["count"] += 1
        if "gutendex.com" in url:
            return FakeResponse(json_data=BOOK_METADATA)
        return FakeResponse(text=RAW_TEXT)

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    book = fetcher.fetch(999, cache_dir=tmp_path)
    assert book["title"] == "Sample Book"
    assert book["author"] == "Sample Author"
    assert book["text"] == "The actual book content goes here."
    assert calls["count"] == 2

    # second call should hit the cache, not the network
    book_again = fetcher.fetch(999, cache_dir=tmp_path)
    assert book_again["text"] == book["text"]
    assert calls["count"] == 2


def test_fetch_refresh_bypasses_cache(tmp_path, monkeypatch):
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        calls["count"] += 1
        if "gutendex.com" in url:
            return FakeResponse(json_data=BOOK_METADATA)
        return FakeResponse(text=RAW_TEXT)

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    fetcher.fetch(999, cache_dir=tmp_path)
    assert calls["count"] == 2
    fetcher.fetch(999, cache_dir=tmp_path, refresh=True)
    assert calls["count"] == 4


def test_fetch_raises_not_found_on_404(tmp_path, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return FakeResponse(status_code=404)

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with pytest.raises(fetcher.BookNotFoundError):
        fetcher.fetch(12345, cache_dir=tmp_path)


def test_fetch_raises_not_found_when_no_plain_text(tmp_path, monkeypatch):
    book_no_txt = {**BOOK_METADATA, "formats": {"application/zip": "https://example.com/book.zip"}}

    def fake_get(url, params=None, timeout=None):
        return FakeResponse(json_data=book_no_txt)

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with pytest.raises(fetcher.BookNotFoundError):
        fetcher.fetch(999, cache_dir=tmp_path)


def test_fetch_raises_fetch_error_on_network_failure(tmp_path, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with pytest.raises(fetcher.BookFetchError):
        fetcher.fetch(999, cache_dir=tmp_path)
