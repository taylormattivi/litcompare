from pathlib import Path

from litcompare import plots


def test_top_words_chart_saves_png(tmp_path):
    top_a = [("fox", 3), ("dog", 2)]
    top_b = [("castle", 3), ("king", 1)]
    path = plots.top_words_chart("Book A", top_a, "Book B", top_b, tmp_path)
    assert Path(path).exists()
    assert Path(path).name == "top_words.png"


def test_metrics_comparison_chart_saves_png(tmp_path):
    stats_a = {"vocabulary_richness": 0.5, "avg_sentence_length": 10.0, "flesch_reading_ease": 70.0}
    stats_b = {"vocabulary_richness": 0.6, "avg_sentence_length": 12.0, "flesch_reading_ease": 60.0}
    path = plots.metrics_comparison_chart("Book A", stats_a, "Book B", stats_b, tmp_path)
    assert Path(path).exists()
    assert Path(path).name == "metrics_comparison.png"


def test_sentence_length_distribution_chart_saves_png(tmp_path):
    path = plots.sentence_length_distribution_chart(
        "Book A", [5, 8, 12, 9], "Book B", [15, 20, 18, 22], tmp_path
    )
    assert Path(path).exists()
    assert Path(path).name == "sentence_length_distribution.png"
