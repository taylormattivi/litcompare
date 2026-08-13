from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

COLOR_A = "#4C72B0"
COLOR_B = "#DD8452"


def _short_label(title, max_len=25):
    return title if len(title) <= max_len else title[: max_len - 1].rstrip() + "…"


def top_words_chart(label_a, top_words_a, label_b, top_words_b, output_dir):
    """Save a side-by-side horizontal bar chart of each book's top words. Returns the PNG path."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, label, pairs, color in zip(axes, (label_a, label_b), (top_words_a, top_words_b), (COLOR_A, COLOR_B)):
        pairs = list(reversed(pairs))
        labels = [w for w, _ in pairs]
        counts = [c for _, c in pairs]
        ax.barh(labels, counts, color=color)
        ax.set_title(label)
        ax.set_xlabel("Count")
    fig.tight_layout()
    path = Path(output_dir) / "top_words.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return str(path)


def metrics_comparison_chart(label_a, stats_a, label_b, stats_b, output_dir):
    """Save a bar chart comparing vocabulary richness, avg sentence length, and readability. Returns the PNG path."""
    metrics = [
        ("Vocabulary richness (TTR)", "vocabulary_richness"),
        ("Avg sentence length", "avg_sentence_length"),
        ("Flesch reading ease", "flesch_reading_ease"),
    ]
    short_a, short_b = _short_label(label_a), _short_label(label_b)
    fig, axes = plt.subplots(1, len(metrics), figsize=(11, 5))
    for ax, (title, key) in zip(axes, metrics):
        ax.bar([short_a, short_b], [stats_a[key], stats_b[key]], color=[COLOR_A, COLOR_B])
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    path = Path(output_dir) / "metrics_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return str(path)


def sentence_length_distribution_chart(label_a, lengths_a, label_b, lengths_b, output_dir):
    """Save an overlaid distribution of sentence lengths for both books. Returns the PNG path."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(lengths_a, color=COLOR_A, label=label_a, alpha=0.5, ax=ax, kde=True, stat="density")
    sns.histplot(lengths_b, color=COLOR_B, label=label_b, alpha=0.5, ax=ax, kde=True, stat="density")
    ax.set_xlabel("Words per sentence")
    ax.set_title("Sentence Length Distribution")
    ax.legend()
    fig.tight_layout()
    path = Path(output_dir) / "sentence_length_distribution.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return str(path)
