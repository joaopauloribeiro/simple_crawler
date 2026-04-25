import html
import logging
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

_IGNORED_SCHEMES = frozenset({"javascript", "mailto", "tel", "data", "ftp", "void"})


class _LinkParser(HTMLParser):
    def __init__(self, base_url: str = "") -> None:
        super().__init__()
        self.base_url = base_url
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []
        self._in_anchor = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            attr_dict = dict(attrs)
            href = attr_dict.get("href") or ""
            if href:
                self._current_href = href
                self._current_text = []
                self._in_anchor = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_anchor:
            if self._current_href:
                resolved = self._resolve(self._current_href)
                if resolved:
                    text = html.unescape("".join(self._current_text).strip())
                    self.links.append((resolved, text))
            self._current_href = None
            self._current_text = []
            self._in_anchor = False

    def handle_data(self, data: str) -> None:
        if self._in_anchor:
            self._current_text.append(data)

    def _resolve(self, href: str) -> str | None:
        href = href.strip()
        if not href or href.startswith("#"):
            return None
        scheme = urlparse(href).scheme.lower()
        if scheme in _IGNORED_SCHEMES:
            return None
        if self.base_url:
            full = urljoin(self.base_url, href)
            return full if urlparse(full).scheme in ("http", "https") else None
        return href if urlparse(href).scheme in ("http", "https") else None


def find_links(filepath: Path | str, base_url: str = "") -> list[tuple[str, str]]:
    """Parse an HTML file and return [(url, link_text), ...]. Never raises."""
    filepath = Path(filepath)
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        logger.error("Cannot read %s: %s", filepath, e)
        return []

    parser = _LinkParser(base_url=base_url)
    try:
        parser.feed(content)
    except Exception as e:
        logger.warning("Parse error in %s: %s", filepath, e)
    return parser.links
