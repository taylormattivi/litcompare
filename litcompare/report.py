from datetime import datetime, timezone
from pathlib import Path


def _stats_table(stats):
    return (
        "| Metric | Value |\n"
        "|---|---|\n"
        f"| Word count | {stats['word_count']:,} |\n"
        f"| Sentence count | {stats['sentence_count']:,} |\n"
        f"| Vocabulary richness (TTR) | {stats['vocabulary_richness']:.3f} |\n"
        f"| Avg sentence length | {stats['avg_sentence_length']:.1f} words |\n"
        f"| Flesch reading ease | {stats['flesch_reading_ease']:.1f} |\n"
    )


def _word_list(pairs, with_score=False):
    if with_score:
        return ", ".join(f"{word} ({score:.3f})" for word, score in pairs)
    return ", ".join(f"{word} ({count})" for word, count in pairs)


def build(book_a, stats_a, book_b, stats_b, distinctive_a, distinctive_b, chart_paths):
    """Assemble the Markdown comparison report as a string. Chart paths are linked by filename,
    so charts must be saved in the same directory the report is written to."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# {book_a['title']} vs. {book_b['title']}",
        "",
        f"*{book_a['title']}* by {book_a['author']} (Gutenberg #{book_a['id']}) compared with "
        f"*{book_b['title']}* by {book_b['author']} (Gutenberg #{book_b['id']}).",
        "",
        f"Generated {generated_at}",
        "",
        "## Statistics",
        "",
        f"### {book_a['title']}",
        "",
        _stats_table(stats_a),
        "",
        f"**Top words:** {_word_list(stats_a['top_words'])}",
        "",
        f"### {book_b['title']}",
        "",
        _stats_table(stats_b),
        "",
        f"**Top words:** {_word_list(stats_b['top_words'])}",
        "",
        "## Distinctive Vocabulary (TF-IDF)",
        "",
        f"**{book_a['title']}:** {_word_list(distinctive_a, with_score=True)}",
        "",
        f"**{book_b['title']}:** {_word_list(distinctive_b, with_score=True)}",
        "",
        "## Charts",
        "",
    ]

    for path in chart_paths:
        name = Path(path).name
        lines.append(f"![{name}]({name})")
        lines.append("")

    return "\n".join(lines)


def write(report_text, output_dir, filename="report.md"):
    """Write the report text to output_dir/filename. Returns the path."""
    path = Path(output_dir) / filename
    path.write_text(report_text, encoding="utf-8")
    return str(path)
