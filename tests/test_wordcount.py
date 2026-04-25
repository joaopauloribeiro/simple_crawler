"""Tests for wordcount."""
from collections import Counter
from pathlib import Path

import pytest

from wordcount import parse_file, top_words, word_count


class TestParseFile:
    def test_basic_word_splitting(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("hello world python", encoding="utf-8")
        assert parse_file(f) == ["hello", "world", "python"]

    def test_repeated_words(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("go go go stop", encoding="utf-8")
        words = parse_file(f)
        assert words.count("go") == 3
        assert words.count("stop") == 1

    def test_punctuation_stripped(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("hello, world! python.", encoding="utf-8")
        words = parse_file(f)
        assert "hello" in words
        assert "world" in words
        assert "python" in words
        assert not any("," in w or "!" in w or "." in w for w in words)

    def test_newlines_treated_as_whitespace(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("line1\nline2\nline3", encoding="utf-8")
        words = parse_file(f)
        assert "line1" in words and "line2" in words and "line3" in words

    def test_accepts_path_object(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("hello", encoding="utf-8")
        assert parse_file(Path(f)) == ["hello"]

    def test_accepts_string_path(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("hello", encoding="utf-8")
        assert parse_file(str(f)) == ["hello"]

    def test_empty_file_returns_empty_list(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("", encoding="utf-8")
        assert parse_file(f) == []


class TestWordCount:
    def test_basic_count(self):
        result = word_count(["a", "b", "a"])
        assert result["a"] == 2
        assert result["b"] == 1

    def test_empty_list(self):
        assert word_count([]) == Counter()

    def test_returns_counter(self):
        assert isinstance(word_count(["x"]), Counter)

    def test_single_word_repeated(self):
        assert word_count(["x"] * 10)["x"] == 10


class TestTopWords:
    def test_top_n_limits_results(self):
        counts = Counter({"a": 10, "b": 8, "c": 5, "d": 2})
        result = top_words(counts, top_n=2)
        assert len(result) == 2
        assert result[0] == ("a", 10)
        assert result[1] == ("b", 8)

    def test_min_count_filters_low_frequency(self):
        counts = Counter({"a": 10, "b": 5, "c": 1})
        result = top_words(counts, min_count=5)
        words = [w for w, _ in result]
        assert "a" in words
        assert "b" in words
        assert "c" not in words

    def test_top_n_and_min_count_combined(self):
        counts = Counter({"a": 10, "b": 7, "c": 5, "d": 3})
        result = top_words(counts, top_n=2, min_count=6)
        assert len(result) == 2
        assert result[0][0] == "a"

    def test_empty_counter_returns_empty(self):
        assert top_words(Counter()) == []

    def test_results_sorted_descending(self):
        counts = Counter({"z": 1, "a": 5, "m": 3})
        result = top_words(counts)
        counts_only = [c for _, c in result]
        assert counts_only == sorted(counts_only, reverse=True)

    def test_no_filters_returns_all(self):
        counts = Counter({"x": 3, "y": 2, "z": 1})
        assert len(top_words(counts)) == 3
