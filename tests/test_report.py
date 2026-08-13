from pathlib import Path

from litcompare import report

BOOK_A = {"title": "Book A", "author": "Author A", "id": 1}
BOOK_B = {"title": "Book B", "author": "Author B", "id": 2}
STATS_A = {
    "word_count": 100,
    "sentence_count": 10,
    "vocabulary_richness": 0.5,
    "avg_sentence_length": 10.0,
    "flesch_reading_ease": 70.0,
    "top_words": [("fox", 3), ("dog", 2)],
}
STATS_B = {
    "word_count": 200,
    "sentence_count": 20,
    "vocabulary_richness": 0.6,
    "avg_sentence_length": 12.0,
    "flesch_reading_ease": 60.0,
    "top_words": [("castle", 3), ("king", 1)],
}
DISTINCTIVE_A = [("fox", 0.5)]
DISTINCTIVE_B = [("castle", 0.6)]
CHART_PATHS = ["/tmp/output/top_words.png", "/tmp/output/metrics_comparison.png"]


def test_build_includes_titles_and_stats():
    text = report.build(BOOK_A, STATS_A, BOOK_B, STATS_B, DISTINCTIVE_A, DISTINCTIVE_B, CHART_PATHS)
    assert "Book A vs. Book B" in text
    assert "fox (3)" in text
    assert "castle (0.600)" in text
    assert "![top_words.png](top_words.png)" in text


def test_write_creates_file(tmp_path):
    path = report.write("# Hello", tmp_path)
    assert Path(path).exists()
    assert Path(path).read_text() == "# Hello"
