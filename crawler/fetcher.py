import logging
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _robots_parser(url: str, user_agent: str, timeout: int) -> urllib.robotparser.RobotFileParser:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_url not in _robots_cache:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception:
            pass
        _robots_cache[robots_url] = rp
    return _robots_cache[robots_url]


def can_fetch(url: str, user_agent: str, timeout: int = 10, respect_robots: bool = True) -> bool:
    if not respect_robots:
        return True
    try:
        rp = _robots_parser(url, user_agent, timeout)
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True


def get_page(
    url: str,
    filepath: Path | str,
    user_agent: str = "SimpleCrawler/2.0",
    timeout: int = 10,
    respect_robots: bool = True,
) -> bool:
    """Download url and save to filepath. Returns True on success."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        logger.warning("Skipping invalid URL: %s", url)
        return False

    if not can_fetch(url, user_agent, timeout, respect_robots):
        logger.info("Blocked by robots.txt: %s", url)
        return False

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            charset = response.headers.get_content_charset("utf-8")
            content = response.read().decode(charset, errors="replace")
        filepath.write_text(content, encoding="utf-8")
        logger.info("Fetched %s -> %s", url, filepath)
        return True
    except urllib.error.HTTPError as e:
        logger.warning("HTTP %d fetching %s", e.code, url)
    except urllib.error.URLError as e:
        logger.warning("URL error fetching %s: %s", url, e.reason)
    except TimeoutError:
        logger.warning("Timeout fetching %s", url)
    except Exception as e:
        logger.error("Unexpected error fetching %s: %s", url, e)
    return False
