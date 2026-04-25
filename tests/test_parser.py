"""Tests for crawler.parser."""
from pathlib import Path

import pytest

from crawler.parser import find_links


def _page(tmp_path: Path, html: str) -> Path:
    p = tmp_path / "page.html"
    p.write_text(html, encoding="utf-8")
    return p


class TestFindLinks:
    def test_extracts_absolute_http_link(self, tmp_path):
        p = _page(tmp_path, '<a href="http://example.com">Example</a>')
        assert ("http://example.com", "Example") in find_links(p)

    def test_extracts_https_link(self, tmp_path):
        p = _page(tmp_path, '<a href="https://secure.org">Secure</a>')
        urls = [u for u, _ in find_links(p)]
        assert "https://secure.org" in urls

    def test_resolves_relative_path(self, tmp_path):
        p = _page(tmp_path, '<a href="/about">About</a>')
        assert ("http://example.com/about", "About") in find_links(p, base_url="http://example.com")

    def test_resolves_relative_path_with_trailing_slash(self, tmp_path):
        p = _page(tmp_path, '<a href="page.html">Page</a>')
        links = find_links(p, base_url="http://example.com/dir/")
        urls = [u for u, _ in links]
        assert "http://example.com/dir/page.html" in urls

    def test_filters_javascript_href(self, tmp_path):
        p = _page(tmp_path, '<a href="javascript:void(0)">Click</a>')
        assert find_links(p) == []

    def test_filters_mailto_href(self, tmp_path):
        p = _page(tmp_path, '<a href="mailto:user@example.com">Mail me</a>')
        assert find_links(p) == []

    def test_filters_tel_href(self, tmp_path):
        p = _page(tmp_path, '<a href="tel:+1234567890">Call</a>')
        assert find_links(p) == []

    def test_filters_fragment_only(self, tmp_path):
        p = _page(tmp_path, '<a href="#section">Jump</a>')
        assert find_links(p) == []

    def test_filters_empty_href(self, tmp_path):
        p = _page(tmp_path, '<a href="">Nothing</a>')
        assert find_links(p) == []

    def test_skips_anchor_with_no_href(self, tmp_path):
        p = _page(tmp_path, '<a name="top">Top</a>')
        assert find_links(p) == []

    def test_unescapes_html_entities_in_text(self, tmp_path):
        p = _page(tmp_path, '<a href="http://example.com">R&amp;D &gt; Lab</a>')
        _, text = find_links(p)[0]
        assert text == "R&D > Lab"

    def test_empty_file_returns_empty_list(self, tmp_path):
        p = _page(tmp_path, "")
        assert find_links(p) == []

    def test_missing_file_returns_empty_list(self, tmp_path):
        assert find_links(tmp_path / "nonexistent.html") == []

    def test_extracts_multiple_links(self, tmp_path):
        p = _page(tmp_path, """
            <a href="http://a.com">A</a>
            <a href="http://b.com">B</a>
            <a href="http://c.com">C</a>
        """)
        urls = {u for u, _ in find_links(p)}
        assert urls == {"http://a.com", "http://b.com", "http://c.com"}

    def test_case_insensitive_tag(self, tmp_path):
        p = _page(tmp_path, '<A HREF="http://example.com">Upper</A>')
        urls = [u for u, _ in find_links(p)]
        assert "http://example.com" in urls

    def test_link_text_stripped(self, tmp_path):
        p = _page(tmp_path, '<a href="http://example.com">  spaces  </a>')
        _, text = find_links(p)[0]
        assert text == "spaces"

    def test_multiline_anchor(self, tmp_path):
        p = _page(tmp_path, '<a\n  href="http://example.com"\n  class="nav">Link</a>')
        urls = [u for u, _ in find_links(p)]
        assert "http://example.com" in urls

    def test_does_not_follow_relative_without_base(self, tmp_path):
        p = _page(tmp_path, '<a href="/path/page.html">No base</a>')
        assert find_links(p) == []
