"""
Word frequency counter.

Usage:
    python wordcount.py <file> [--top N] [--min-count N] [--total]

Examples:
    python wordcount.py page.html                # all words, sorted by frequency
    python wordcount.py page.html --top 20       # top 20 words
    python wordcount.py page.html --min-count 5  # words appearing ≥ 5 times
    python wordcount.py page.html --top 10 --total
"""
import argparse
from collections import Counter
from pathlib import Path

_PUNCTUATION = ',.;:~^]}[{=+-_()<>|\\/*&%$#@!"\'?'


def parse_file(filepath: str | Path) -> list[str]:
    text = Path(filepath).read_text(encoding="latin-1", errors="replace")
    for char in _PUNCTUATION:
        text = text.replace(char, " ")
    return text.split()


def word_count(words: list[str]) -> Counter[str]:
    return Counter(words)


def top_words(
    counts: Counter[str],
    top_n: int | None = None,
    min_count: int | None = None,
) -> list[tuple[str, int]]:
    result = counts.most_common()
    if min_count is not None:
        result = [(w, c) for w, c in result if c >= min_count]
    if top_n is not None:
        result = result[:top_n]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count word frequencies in a text file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("filename", help="File to analyse")
    parser.add_argument("--top", type=int, metavar="N",
                        help="Show only the top N words by frequency")
    parser.add_argument("--min-count", type=int, metavar="N",
                        help="Exclude words appearing fewer than N times")
    parser.add_argument("--total", action="store_true",
                        help="Print the total word count at the end")
    args = parser.parse_args()

    words = parse_file(args.filename)
    counts = word_count(words)
    results = top_words(counts, top_n=args.top, min_count=args.min_count)

    for word, count in results:
        print(f"{word}: {count}")

    if args.total:
        print(f"\nTotal words shown: {sum(c for _, c in results)}")
        print(f"Unique words in file: {len(counts)}")


if __name__ == "__main__":
    main()
