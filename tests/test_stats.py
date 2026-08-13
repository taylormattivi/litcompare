from pathlib import Path

from litcompare import stats
from litcompare.fetcher import _strip_boilerplate

FIXTURES = Path(__file__).parent / "fixtures"
TEXT_A = _strip_boilerplate((FIXTURES / "sample_a.txt").read_text())
TEXT_B = _strip_boilerplate((FIXTURES / "sample_b.txt").read_text())


def test_vocabulary_richness_all_unique_words():
    assert stats.vocabulary_richness(["a", "b", "c"]) == 1.0


def test_vocabulary_richness_with_repeats():
    assert stats.vocabulary_richness(["a", "a", "b", "b"]) == 0.5


def test_vocabulary_richness_empty_list():
    assert stats.vocabulary_richness([]) == 0.0


def test_avg_sentence_length():
    words = ["a"] * 10
    sentences = ["s1", "s2"]
    assert stats.avg_sentence_length(words, sentences) == 5.0


def test_flesch_reading_ease_returns_zero_for_empty_input():
    assert stats.flesch_reading_ease([], []) == 0.0


def test_top_words_filters_stopwords_and_pronouns():
    words = ["the", "fox", "fox", "he", "ran", "ran", "ran"]
    result = stats.top_words(words, n=5)
    assert ("the", 1) not in result
    assert ("he", 1) not in result
    assert result[0] == ("ran", 3)


def test_analyze_returns_expected_keys():
    result = stats.analyze(TEXT_A, top_n=5)
    expected_keys = {
        "word_count", "sentence_count", "vocabulary_richness",
        "avg_sentence_length", "flesch_reading_ease", "top_words", "sentence_lengths",
    }
    assert expected_keys.issubset(result.keys())
    assert result["word_count"] > 0
    assert result["sentence_count"] > 0
    assert len(result["sentence_lengths"]) == result["sentence_count"]


def test_distinctive_words_returns_terms_specific_to_each_text():
    distinctive_a, distinctive_b = stats.distinctive_words(TEXT_A, TEXT_B, n=5)
    words_a = {w for w, _ in distinctive_a}
    words_b = {w for w, _ in distinctive_b}
    assert "fox" in words_a
    assert "castle" in words_b
    assert words_a.isdisjoint(words_b)
