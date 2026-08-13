from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer

from litcompare.cleaner import sentences, words

STOPWORDS = {
    # Articles
    "a", "an", "the",

    # Conjunctions
    "and", "but", "or", "nor", "so", "yet", "for", "because", "although",
    "though", "while", "whereas", "if", "unless", "until", "than", "whether",
    "as",

    # Prepositions
    "of", "in", "on", "at", "to", "from", "by", "with", "without", "about",
    "above", "below", "under", "over", "into", "onto", "upon", "through",
    "during", "before", "after", "between", "among", "against", "toward",
    "towards", "within", "beyond", "across", "behind", "beside", "near",

    # Auxiliary & modal verbs
    "be", "am", "is", "are", "was", "were", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing",
    "will", "would", "shall", "should", "can", "could", "may", "might",
    "must", "ought",

    # Determiners, quantifiers, common adverbs
    "not", "no", "all", "any", "some", "each", "every", "either", "neither",
    "both", "few", "many", "much", "most", "more", "less", "least", "such",
    "same", "other", "another", "own", "very", "too", "only", "just", "even",
    "still", "also", "then", "there", "here", "where", "when", "why", "how",
    "again", "once", "ever", "never", "always", "often", "now", "thus",
    "quite", "rather", "somewhat", "up", "down", "out", "off",

    # Leftover tokenization fragments (curly apostrophes in contractions like
    # it's, don't, we'll split into a bare consonant/vowel remainder)
    "s", "t", "d", "ll", "re", "ve", "m",

    # Archaic / poetic function words (common in older Gutenberg texts)
    "thou", "thee", "thy", "thine", "thyself", "ye", "hath", "hast",
    "doth", "dost", "shalt", "wilt", "canst", "unto", "whilst", "amongst",
    "betwixt", "ere", "nay", "yea", "o", "oh", "hither", "thither",
    "whither", "hence", "thence", "whence",

    # Demonstrative / relative / interrogative pronouns
    "this", "that", "these", "those", "which", "who", "whom", "whose", "what",

    # Titles
    "mr", "mrs", "ms", "miss", "dr",

    # Common narrative verbs
    "said",
}

PRONOUNS = {
    "i", "me", "my", "mine", "myself",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "it", "its", "itself",
    "we", "us", "our", "ours", "ourselves",
    "they", "them", "their", "theirs", "themselves",
}


def _count_syllables(word):
    """Estimate syllable count in a word using a vowel-group heuristic."""
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def top_words(word_list, n=15):
    """Return the n most common non-stopword, non-pronoun words as (word, count) pairs."""
    filtered = [w for w in word_list if w not in STOPWORDS and w not in PRONOUNS]
    return Counter(filtered).most_common(n)


def vocabulary_richness(word_list):
    """Return the type-token ratio: unique words / total words."""
    if not word_list:
        return 0.0
    return len(set(word_list)) / len(word_list)


def avg_sentence_length(word_list, sentence_list):
    """Return the average number of words per sentence."""
    if not sentence_list:
        return 0.0
    return len(word_list) / len(sentence_list)


def flesch_reading_ease(word_list, sentence_list):
    """Return the Flesch Reading Ease score (higher = easier to read)."""
    if not word_list or not sentence_list:
        return 0.0
    syllables = sum(_count_syllables(w) for w in word_list)
    words_per_sentence = len(word_list) / len(sentence_list)
    syllables_per_word = syllables / len(word_list)
    return 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word


def analyze(text, top_n=15):
    """Compute standalone statistics for a single text. Returns a dict."""
    word_list = words(text)
    sentence_list = sentences(text)
    sentence_lengths = [len(words(s)) for s in sentence_list]
    return {
        "word_count": len(word_list),
        "sentence_count": len(sentence_list),
        "vocabulary_richness": vocabulary_richness(word_list),
        "avg_sentence_length": avg_sentence_length(word_list, sentence_list),
        "flesch_reading_ease": flesch_reading_ease(word_list, sentence_list),
        "top_words": top_words(word_list, n=top_n),
        "sentence_lengths": sentence_lengths,
    }


def distinctive_words(text_a, text_b, n=15):
    """Return the n most distinctive words for each text via TF-IDF, as (word, score) pairs."""
    vectorizer = TfidfVectorizer(stop_words=list(STOPWORDS | PRONOUNS), token_pattern=r"[a-zA-Z]+")
    matrix = vectorizer.fit_transform([text_a, text_b])
    terms = vectorizer.get_feature_names_out()

    def top_for_row(row_index):
        row = matrix[row_index].toarray().ravel()
        top_indices = row.argsort()[::-1][:n]
        return [(terms[i], round(float(row[i]), 4)) for i in top_indices if row[i] > 0]

    return top_for_row(0), top_for_row(1)
