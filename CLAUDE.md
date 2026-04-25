# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A modernised educational web crawler (Python 3.10+). It fetches seed URLs, extracts hyperlinks using `html.parser`, respects `robots.txt`, rate-limits requests per host, and stores discovered links in SQLite. All dependencies are Python standard library only.

## Commands

```bash
# Run tests (requires pytest)
pip install pytest
pytest                          # all 66 tests, verbose
pytest tests/test_storage.py    # single module

# Run the crawler
python webcrawler.py
python webcrawler.py --seeds https://example.com --db my.db --delay 2.0
python webcrawler.py --help

# Word frequency tool
python wordcount.py somefile.txt --top 20 --min-count 3

# Python concepts quiz (interactive CLI)
python quiz/python_concepts_quiz.py
python quiz/python_concepts_quiz.py --shuffle
python quiz/python_concepts_quiz.py --topic pathlib
```

## Architecture

Two-phase crawl orchestrated by `webcrawler.py`:

1. **Primary discovery** — fetch each seed with `crawler.fetcher.get_page()`, parse links with `crawler.parser.find_links()`, accumulate in `primary` dict keyed by discovered URL.
2. **Secondary discovery** — fetch each primary link, parse again, accumulate only URLs not seen in phase 1 into `secondary` dict.
3. **Persistence** — batch-insert all `(source, link)` pairs via `crawler.storage.CrawlerDB.insert_links_batch()`.

Module responsibilities:

| Module | Role |
|---|---|
| `crawler/config.py` | `CrawlerConfig` dataclass; default seed list |
| `crawler/fetcher.py` | HTTP download with timeout, `User-Agent`, robots.txt cache, URL validation |
| `crawler/parser.py` | `HTMLParser`-based `<a href>` extraction; resolves relative URLs; filters non-HTTP schemes |
| `crawler/storage.py` | SQLite context manager; `INSERT OR IGNORE`; indexes on `page` and `link`; batch commit |
| `wordcount.py` | Standalone CLI: word frequency via `collections.Counter` + `argparse` |
| `quiz/python_concepts_quiz.py` | Interactive 20-question quiz on Python 3.4–3.12 features |

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS ref_links (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    page    TEXT NOT NULL,
    link    TEXT NOT NULL,
    date    TEXT NOT NULL,
    UNIQUE(page, link)
);
CREATE INDEX IF NOT EXISTS idx_ref_page ON ref_links(page);
CREATE INDEX IF NOT EXISTS idx_ref_link ON ref_links(link);

CREATE TABLE IF NOT EXISTS crawl_log (
    url        TEXT PRIMARY KEY,
    fetched_at TEXT NOT NULL,
    status     TEXT NOT NULL
);
```

## Key Design Decisions

- **No bare `except:`** — all exception handling names specific types (`urllib.error.HTTPError`, `urllib.error.URLError`, `TimeoutError`, `OSError`).
- **`CrawlerDB` is a context manager** — the SQLite connection is created in `__enter__` and closed in `__exit__`. Never import at module level.
- **`INSERT OR IGNORE`** — deduplication is enforced by the `UNIQUE(page, link)` constraint, not in Python.
- **`html.parser` not regex** — `_LinkParser` subclasses `HTMLParser`, which handles multi-line tags, attributes before `href`, and nested tags correctly.
- **`html.unescape()`** — replaces the old hand-rolled `html_unescape.py`; available in stdlib since Python 3.4.
- **`pathlib.Path` throughout** — no string concatenation for file paths; `mkdir(parents=True, exist_ok=True)` prevents missing-directory crashes.

## Python Version

Python 3.10 minimum (`pyproject.toml` enforces `requires-python = ">=3.10"`). The `X | Y` union type syntax and `match`/`case` are used.

## Files No Longer in the Codebase

`get_page.py`, `find_links.py`, `html_unescape.py`, `url_store.py` — superseded by the `crawler/` package. `categorizer.py`, `sqlite3sheel.py`, `util/url_store.py` — removed (empty stub, Python 2-only shell, development scratch).

## Additional Documentation

- `docs/MODERNIZATION.md` — step-by-step record of every change from the 2012 original.
- `docs/CRAWLER_USES_REPORT.md` — analytical report on modern use-cases for web crawlers.

## GitHub Actions

`.github/workflows/matrix-example.yml` is an educational example of the matrix strategy feature. It triggers only on the `new_action` branch and is not part of the development workflow.
