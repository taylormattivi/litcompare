import argparse
import sys
from pathlib import Path

from litcompare import plots, report, stats
from litcompare.fetcher import BookFetchError, BookNotFoundError, fetch


def _positive_int(value):
    """argparse type: reject zero, negative, or non-integer values with a clean CLI error."""
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"must be a positive integer, got {ivalue}")
    return ivalue


def compare_command(args):
    output_dir = Path(args.output_dir or f"output/{args.id1}_vs_{args.id2}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching book {args.id1}...")
    try:
        book_a = fetch(args.id1, cache_dir=args.cache_dir, refresh=args.refresh)
    except (BookNotFoundError, BookFetchError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Fetching book {args.id2}...")
    try:
        book_b = fetch(args.id2, cache_dir=args.cache_dir, refresh=args.refresh)
    except (BookNotFoundError, BookFetchError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"{book_a['title']} by {book_a['author']}")
    print(f"{book_b['title']} by {book_b['author']}")

    print("Computing statistics...")
    stats_a = stats.analyze(book_a["text"], top_n=args.top_n)
    stats_b = stats.analyze(book_b["text"], top_n=args.top_n)
    distinctive_a, distinctive_b = stats.distinctive_words(book_a["text"], book_b["text"], n=args.top_n)

    print("Generating charts...")
    chart_paths = [
        plots.top_words_chart(book_a["title"], stats_a["top_words"], book_b["title"], stats_b["top_words"], output_dir),
        plots.metrics_comparison_chart(book_a["title"], stats_a, book_b["title"], stats_b, output_dir),
        plots.sentence_length_distribution_chart(
            book_a["title"], stats_a["sentence_lengths"], book_b["title"], stats_b["sentence_lengths"], output_dir
        ),
    ]

    print("Writing report...")
    report_text = report.build(book_a, stats_a, book_b, stats_b, distinctive_a, distinctive_b, chart_paths)
    report_path = report.write(report_text, output_dir)

    print(f"\nDone: {report_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(prog="litcompare")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare_parser = subparsers.add_parser("compare", help="compare two books by Project Gutenberg ID")
    compare_parser.add_argument("id1", type=_positive_int, help="Project Gutenberg ID of the first book")
    compare_parser.add_argument("id2", type=_positive_int, help="Project Gutenberg ID of the second book")
    compare_parser.add_argument("-o", "--output-dir", help="directory for the report and charts (default: output/<id1>_vs_<id2>/)")
    compare_parser.add_argument("--top-n", type=_positive_int, default=15, help="number of top words per book (default: 15)")
    compare_parser.add_argument("--cache-dir", default=".cache", help="directory for cached downloads (default: .cache/)")
    compare_parser.add_argument("--refresh", action="store_true", help="bypass the cache and re-download both texts")

    args = parser.parse_args()

    if args.command == "compare":
        sys.exit(compare_command(args))


if __name__ == "__main__":
    main()
