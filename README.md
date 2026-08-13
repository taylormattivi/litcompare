# litcompare

A command-line tool that fetches two books from Project Gutenberg and produces a comparative
analysis — vocabulary, sentence structure, readability, and distinctive vocabulary — as a Markdown
report with embedded charts.

## Why I built this

<!-- TODO: fill this in -->

## Features

- Fetch any two books by Project Gutenberg ID, with local caching and boilerplate stripped
- Compute vocabulary richness, average sentence length, Flesch reading ease, and top-word frequencies
- Surface each book's most distinctive vocabulary via TF-IDF
- Generate comparison charts (top words, metrics, sentence-length distribution)
- Assemble everything into a single Markdown report

## Installation

```bash
git clone <repo-url>
cd litcompare
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

```bash
litcompare compare 14591 75778
```

This compares *Faust, Part I* (trans. Bayard Taylor) with *The Book of Job*, and writes a report to
`output/14591_vs_75778/report.md` along with the chart PNGs it references.

Options:

```
litcompare compare <id1> <id2>
    -o, --output-dir PATH    directory for the report and charts (default: output/<id1>_vs_<id2>/)
    --top-n N                 number of top words per book (default: 15)
    --cache-dir PATH          directory for cached downloads (default: .cache/)
    --refresh                   bypass the cache and re-download both texts
```

## How it works

1. **Fetch** — looks up each book's metadata and plain-text URL via the [Gutendex](https://gutendex.com)
   API, downloads it, strips Project Gutenberg's standard boilerplate, and caches the result locally.
2. **Clean** — tokenizes the text into words and sentences with NLTK.
3. **Analyze** — computes vocabulary richness, average sentence length, Flesch reading ease, top-word
   frequencies, and TF-IDF-based distinctive vocabulary between the two books.
4. **Plot** — renders comparison charts to PNG files (matplotlib + seaborn, no GUI backend).
5. **Report** — assembles everything into a single Markdown file with the charts embedded.

## Running tests

```bash
pytest
```

Tests run entirely offline — no network calls.
