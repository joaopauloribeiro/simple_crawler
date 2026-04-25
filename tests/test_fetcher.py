"""Tests for crawler.fetcher."""
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from crawler.fetcher import can_fetch, get_page


def _mock_response(body: bytes = b"<html></html>", charset: str = "utf-8") -> MagicMock:
    r = MagicMock()
    r.read.return_value = body
    r.headers.get_content_charset.return_value = charset
    r.__enter__ = lambda s: s
    r.__exit__ = MagicMock(return_value=False)
    return r


class TestGetPage:
    def test_rejects_non_http_scheme(self, tmp_path):
        assert get_page("ftp://example.com", tmp_path / "out.html") is False

    def test_rejects_missing_scheme(self, tmp_path):
        assert get_page("example.com", tmp_path / "out.html") is False

    def test_rejects_javascript_url(self, tmp_path):
        assert get_page("javascript:void(0)", tmp_path / "out.html") is False

    def test_rejects_empty_string(self, tmp_path):
        assert get_page("", tmp_path / "out.html") is False

    def test_successful_download_returns_true(self, tmp_path):
        out = tmp_path / "page.html"
        with patch("urllib.request.urlopen", return_value=_mock_response(b"<b>hi</b>")):
            result = get_page("http://example.com", out, respect_robots=False)
        assert result is True

    def test_successful_download_writes_content(self, tmp_path):
        out = tmp_path / "page.html"
        with patch("urllib.request.urlopen", return_value=_mock_response(b"<p>hello</p>")):
            get_page("http://example.com", out, respect_robots=False)
        assert out.read_text() == "<p>hello</p>"

    def test_creates_missing_parent_directories(self, tmp_path):
        out = tmp_path / "deep" / "nested" / "page.html"
        with patch("urllib.request.urlopen", return_value=_mock_response()):
            get_page("http://example.com", out, respect_robots=False)
        assert out.parent.exists()

    def test_http_404_returns_false(self, tmp_path):
        with patch("urllib.request.urlopen",
                   side_effect=urllib.error.HTTPError(None, 404, "Not Found", {}, None)):
            result = get_page("http://example.com", tmp_path / "out.html", respect_robots=False)
        assert result is False

    def test_url_error_returns_false(self, tmp_path):
        with patch("urllib.request.urlopen",
                   side_effect=urllib.error.URLError("connection refused")):
            result = get_page("http://example.com", tmp_path / "out.html", respect_robots=False)
        assert result is False

    def test_timeout_returns_false(self, tmp_path):
        with patch("urllib.request.urlopen", side_effect=TimeoutError()):
            result = get_page("http://example.com", tmp_path / "out.html", respect_robots=False)
        assert result is False

    def test_robots_blocked_returns_false(self, tmp_path):
        with patch("crawler.fetcher.can_fetch", return_value=False):
            result = get_page("http://example.com/private", tmp_path / "out.html",
                               respect_robots=True)
        assert result is False

    def test_latin1_page_decoded_correctly(self, tmp_path):
        out = tmp_path / "page.html"
        # latin-1 byte 0xe9 = é
        with patch("urllib.request.urlopen",
                   return_value=_mock_response(b"caf\xe9", charset="latin-1")):
            get_page("http://example.com", out, respect_robots=False)
        assert "café" in out.read_text(encoding="utf-8")


class TestCanFetch:
    def test_returns_true_when_robots_disabled(self):
        assert can_fetch("http://example.com", "bot", respect_robots=False) is True

    def test_returns_true_on_robots_fetch_failure(self):
        with patch("crawler.fetcher._robots_parser",
                   side_effect=Exception("network error")):
            assert can_fetch("http://example.com", "bot", respect_robots=True) is True
