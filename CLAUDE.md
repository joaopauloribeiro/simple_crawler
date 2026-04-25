# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A minimal educational web crawler (~2012) that fetches seed URLs, extracts hyperlinks via regex, and stores them in SQLite3. All dependencies are Python standard library only (`sqlite3`, `urllib`, `re`, `sys`, `html.entities`). There is no packaging, no `requirements.txt`, and no test suite.

## Running the Crawler

```bash
python webcrawler.py
```

Seed URLs are hardcoded at the top of `webcrawler.py`. Edit that array to change crawl targets.

## Architecture

The crawl runs in two phases, both orchestrated by `webcrawler.py`:

1. **Primary discovery** — fetch each seed URL with `get_page.get_page()`, parse links with `find_links.find_links()`, accumulate in a dict keyed by source URL.
2. **Secondary discovery** — for every link found in phase 1, fetch and parse again, accumulating a second dict.
3. **Persistence** — insert all secondary links into SQLite via `url_store.insert_url()`.

Module responsibilities:
- `get_page.py` — downloads a URL and saves it to a local file; returns 0 on success, -1 on failure.
- `find_links.py` — regex-based `<a href>` extraction; returns `[(url, link_text), ...]`. Depends on `html_unescape.py`.
- `html_unescape.py` — converts numeric and named HTML entities to Unicode.
- `url_store.py` — thin SQLite3 wrapper; exposes `init_db()`, `insert_url()`, `get_link()`, `get_urls()`, `dump_data()`, `close_db()`. Uses a module-level global `conn`.
- `wordcount.py` — standalone CLI tool; reads a crawled file and prints word frequencies.

Files that are **not part of the active codebase**: `categorizer.py` (empty stub), `sqlite3sheel.py` (Python 2–only interactive SQL shell), `util/url_store.py` (development scratch file), `perl/urldump.pl` (legacy Perl reference).

## Python 2/3 Compatibility

The code conditionally imports `urllib` vs `urllib.request` and `htmlentitydefs` vs `html.entities` based on `sys.version_info`. Preserve this pattern when modifying those files.

## Database Schema

Single table in `links.db` (created at runtime):

```sql
CREATE TABLE ref_links (page TEXT, link TEXT, date TEXT)
```

No indexes. The database file is not committed to the repo.

## GitHub Actions

`.github/workflows/matrix-example.yml` is an educational example of the matrix strategy feature. It triggers only on the `new_action` branch and contains no crawler-specific build or test steps—it is not part of the development workflow.
