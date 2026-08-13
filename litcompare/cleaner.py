import nltk

_NLTK_RESOURCES = ("punkt_tab", "punkt")
_ready = False


def ensure_nltk_data():
    """Download the NLTK tokenizer data if it isn't already present, once per process.

    nltk.download() checks locally first and is a no-op when the resource is already
    present, so this is cheap to call unconditionally.
    """
    global _ready
    if _ready:
        return
    for resource in _NLTK_RESOURCES:
        nltk.download(resource, quiet=True)
    _ready = True


def sentences(text):
    """Split text into a list of sentences."""
    ensure_nltk_data()
    return nltk.sent_tokenize(text)


def words(text):
    """Split text into lowercase alphabetic word tokens (punctuation and digits dropped)."""
    ensure_nltk_data()
    tokens = nltk.word_tokenize(text)
    return [token.lower() for token in tokens if token.isalpha()]
