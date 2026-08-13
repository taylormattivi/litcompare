from litcompare import cleaner


def test_words_lowercases_and_drops_punctuation():
    tokens = cleaner.words("The Fox, the Dog -- and 42 cats!")
    assert tokens == ["the", "fox", "the", "dog", "and", "cats"]


def test_sentences_splits_on_boundaries():
    text = "The fox ran. The dog slept! Did the cat watch?"
    result = cleaner.sentences(text)
    assert len(result) == 3
    assert result[0].startswith("The fox ran")
