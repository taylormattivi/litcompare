import json
import re
from pathlib import Path

import requests

GUTENDEX_BOOK_URL = "https://gutendex.com/books/{id}"
REQUEST_TIMEOUT = 30

_BOILERPLATE_RE = re.compile(
    r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*(.*?)"
    r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK",
    re.DOTALL,
)


class BookNotFoundError(Exception):
    """Raised when a Gutenberg ID has no matching book or no plain-text edition."""


class BookFetchError(Exception):
    """Raised when a network request to Gutendex or Gutenberg fails."""


def _strip_boilerplate(text):
    """Return only the text between Project Gutenberg's START/END markers, or the original text if not found."""
    match = _BOILERPLATE_RE.search(text)
    if match:
        return match.group(1).strip()
    return text


def _get_plain_text_url(book):
    """Return the plain-text (non-zip) download URL from a book's formats, or None."""
    for mime_type, url in book["formats"].items():
        if mime_type.startswith("text/plain") and not url.endswith(".zip"):
            return url
    return None


def _fetch_metadata(gutenberg_id):
    try:
        response = requests.get(
            GUTENDEX_BOOK_URL.format(id=gutenberg_id), timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as exc:
        raise BookFetchError(f"Could not reach Gutendex for book {gutenberg_id}: {exc}") from exc

    if response.status_code == 404:
        raise BookNotFoundError(f"No Gutenberg book found with ID {gutenberg_id}.")
    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        raise BookFetchError(f"Gutendex returned an error for book {gutenberg_id}: {exc}") from exc

    return response.json()


def _download_text(url):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise BookFetchError(f"Could not download text from {url}: {exc}") from exc
    response.encoding = "utf-8"
    return response.text


def fetch(gutenberg_id, cache_dir=".cache", refresh=False):
    """Fetch a book by Gutenberg ID, using the local cache unless refresh is True.

    Returns a dict with keys: id, title, author, text (boilerplate stripped).
    Raises BookNotFoundError or BookFetchError on failure.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    text_path = cache_dir / f"{gutenberg_id}.txt"
    meta_path = cache_dir / f"{gutenberg_id}.json"

    if not refresh and text_path.exists() and meta_path.exists():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        text = text_path.read_text(encoding="utf-8")
        return {**metadata, "text": text}

    book = _fetch_metadata(gutenberg_id)
    url = _get_plain_text_url(book)
    if url is None:
        raise BookNotFoundError(f"No plain-text format available for '{book['title']}' (ID {gutenberg_id}).")

    text = _strip_boilerplate(_download_text(url))
    authors = book.get("authors") or []
    metadata = {
        "id": gutenberg_id,
        "title": book["title"],
        "author": authors[0]["name"] if authors else "Unknown",
    }

    text_path.write_text(text, encoding="utf-8")
    meta_path.write_text(json.dumps(metadata), encoding="utf-8")

    return {**metadata, "text": text}
