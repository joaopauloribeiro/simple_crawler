# Modernization Technical Document

A step-by-step record of every change made when modernising `simple_crawler`
from its 2012 Python 2/3 dual-mode codebase to a clean Python 3.10+ package.

---

## 1  Project Structure

### Old layout (flat, no package)

```
webcrawler.py   get_page.py   find_links.py
html_unescape.py  url_store.py  wordcount.py
```

No `__init__.py`, no namespace, no installable entry point. Running tests
required adding the repo root to `PYTHONPATH` manually.

### New layout (package-based)

```
crawler/
  __init__.py  config.py  fetcher.py  parser.py  storage.py
tests/
  test_fetcher.py  test_parser.py  test_storage.py  test_wordcount.py
docs/  quiz/
wordcount.py  webcrawler.py  pyproject.toml
```

A proper package allows relative imports, makes `pytest` discovery automatic,
and supports `pip install -e .` without manipulating `PYTHONPATH`.

---

## 2  Files Removed (superseded)

| File | Reason |
|---|---|
| `get_page.py` | Superseded by `crawler/fetcher.py` |
| `find_links.py` | Superseded by `crawler/parser.py` |
| `html_unescape.py` | `html.unescape()` has been in stdlib since Python 3.4 |
| `url_store.py` | Superseded by `crawler/storage.py` |
| `categorizer.py` | Empty stub, never implemented |
| `sqlite3sheel.py` | Python 2-only syntax; replaced by `python -m sqlite3` (built-in since 3.12) |
| `util/url_store.py` | Development scratch file with import-time side effects |

---

## 3  Bug Fixes

### 3.1  Bare `except:` clauses (silent failure)

**Before** — `webcrawler.py`, `get_page.py`:
```python
try:
    page_flag = get_page.get_page(seed['page'], seed['file'])
except:          # catches BaseException — including KeyboardInterrupt, SystemExit
    continue
```
Pressing Ctrl-C had no effect. Any internal `TypeError` or `AttributeError`
was swallowed with no indication of what went wrong.

**After** — specific exception types only:
```python
except urllib.error.HTTPError as e:
    logger.warning("HTTP %d fetching %s", e.code, url)
except urllib.error.URLError as e:
    logger.warning("URL error fetching %s: %s", url, e.reason)
except TimeoutError:
    logger.warning("Timeout fetching %s", url)
```

### 3.2  Resource leaks (file handles never closed)

**Before** — `find_links.py`:
```python
page = open(filename, "rt").read()   # handle leaked to GC
```

**Before** — `get_page.py`:
```python
file_save = open(filename, "wt")
file_save.write(page.read().decode("latin-1"))
file_save.close()    # never reached if decode() raises
```

**After** — all file I/O uses `pathlib` or `with` blocks:
```python
content = filepath.read_text(encoding="utf-8", errors="replace")
filepath.write_text(content, encoding="utf-8")

with urllib.request.urlopen(req, timeout=timeout) as response:
    content = response.read().decode(charset, errors="replace")
```

### 3.3  Broken secondary-links logic

**Before** — `webcrawler.py`:
```python
secondary_links = stored_links.copy()   # copy of { link -> seed }
for seed in stored_links:               # iterates PRIMARY links
    ...
    for link in seed_links:
        if link[0] not in secondary_links:   # checked against copy
            secondary_links[link[0]] = seed
```
Seeds themselves end up in `secondary_links` with themselves as their own
source. Any primary link found again during phase 2 overwrote the original
source record.

**After** — `webcrawler.py`:
```python
primary: dict[str, str] = {}    # discovered_url -> seed

# Phase 2 starts fresh — no copy of primary
secondary: dict[str, str] = {}  # discovered_url -> primary_page

for primary_url, _ in primary.items():
    for url, _ in find_links(page_file, base_url=primary_url):
        if url not in primary:          # only truly new URLs
            secondary.setdefault(url, primary_url)
```

### 3.4  URL validation with `re.match`

**Before** — `get_page.py`:
```python
if re.match(r'http[s]?://...', url, flags=re.IGNORECASE):
```
`re.match` anchors only at the **start**. A URL ending with arbitrary garbage
still passed. More critically, it did not reject `javascript:` hrefs or
bare paths.

**After** — `crawler/fetcher.py`:
```python
def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
```
`urlparse` is the correct tool: it normalises, deconstructs, and handles
edge cases that regex cannot.

### 3.5  Filename race condition in phase 2

**Before** — `webcrawler.py`:
```python
def random_file(link):
    return "html/test_" + str(int(time.time())) + ".html"
```
Two consecutive calls within the same second return the **same filename**,
causing the second download to overwrite the first.

**After** — `webcrawler.py` uses a sequential counter:
```python
page_file = config.output_dir / f"p2_{idx:05d}.html"
```
Each secondary page gets a unique zero-padded index that is also human-readable.

### 3.6  Import-time database connection side effect

**Before** — `url_store.py` (line 10):
```python
conn = sqlite3.connect('webcrawler.db')   # executed at import time
```
Any module that imported `url_store` — including tests — immediately created or
opened `webcrawler.db` in the current working directory. Testability was zero.

**After** — `crawler/storage.py`:
```python
class CrawlerDB:
    def __init__(self, db_path: Path | str = "crawler.db") -> None:
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None   # not opened yet

    def __enter__(self) -> "CrawlerDB":
        self._conn = sqlite3.connect(self.db_path)     # opened here
        ...
```
The connection is created only when the context manager is entered, and closed
when it exits — making every test fully isolated via `tmp_path`.

### 3.7  Deprecated APIs

| Old code | Issue | Fix |
|---|---|---|
| `open(f, 'rU')` | Removed in Python 3.11 | `Path(f).read_text()` |
| `sqlite3.OptimizedUnicode` | Removed in Python 3.13 | Dropped (str is default) |
| `unichr()` | Python 2 only | `chr()` (or removed; `html.unescape` replaces the module) |
| `urllib.urlopen()` | Python 2 only | `urllib.request.urlopen()` |
| `htmlentitydefs` | Python 2 only | `html.entities` (or removed) |

---

## 4  Python 3.10+ Modernisations

### 4.1  Python 2 compatibility shims removed

All `if PYTHON_VERSION <= 2:` blocks, `PYTHON_VERSION = list(sys.version_info)[0]`
globals, `unichr`, and Python 2 import aliases have been deleted.
`pyproject.toml` enforces `requires-python = ">=3.10"`.

### 4.2  Type hints (PEP 484/526/604)

All public function signatures carry full annotations. The `X | Y` union
syntax (Python 3.10) replaces `Optional[X]` and `Union[X, Y]`:

```python
# Before (no annotations)
def get_page(url, filename):

# After
def get_page(
    url: str,
    filepath: Path | str,
    user_agent: str = "SimpleCrawler/2.0",
    timeout: int = 10,
    respect_robots: bool = True,
) -> bool:
```

### 4.3  Dataclasses (PEP 557, Python 3.7)

`CrawlerConfig` is a `@dataclass` — no boilerplate `__init__`, immutable
defaults are expressed with `field(default_factory=...)`:

```python
@dataclass
class CrawlerConfig:
    seeds: list[str] = field(default_factory=lambda: ["https://..."])
    db_path: Path = field(default_factory=lambda: Path("crawler.db"))
    request_timeout: int = 10
    respect_robots: bool = True
```

### 4.4  `pathlib.Path` throughout (PEP 428, Python 3.4)

String path concatenation replaced with `Path` objects and the `/` operator:

```python
# Before
"html/test_" + str(int(time.time())) + ".html"

# After
config.output_dir / f"p2_{idx:05d}.html"
```
`mkdir(parents=True, exist_ok=True)`, `read_text()`, and `write_text()` replace
manual directory creation and `open()` calls.

### 4.5  `argparse` (Python 3.2, but not used in original)

Both `webcrawler.py` and `wordcount.py` now expose proper CLIs:

```
python webcrawler.py --seeds https://a.com https://b.com \
    --db mydb.db --timeout 15 --delay 0.5 --max-pages 100 --no-robots
```

### 4.6  Structured logging

All `print()` statements replaced with `logging.getLogger(__name__)`:

```python
logger = logging.getLogger(__name__)
logger.info("Fetched %s -> %s", url, filepath)
logger.warning("HTTP %d fetching %s", e.code, url)
```
The root logger is configured once in `webcrawler.py` via `logging.basicConfig`.
Log level is controllable; `--debug` flag sets `logging.DEBUG`.

### 4.7  `html.parser` replaces regex-based link extraction

**Before** — `find_links.py`:
```python
links = re.findall(r'<a.*?href=[\'"]([^#].*?)[\'"].*?>(.*?)</a>', page)
```
This breaks on: multi-line tags, attributes before `href`, single-quoted hrefs,
nested tags inside link text, and self-closing variants.

**After** — `crawler/parser.py` subclasses `html.parser.HTMLParser`:
```python
class _LinkParser(HTMLParser):
    def handle_starttag(self, tag, attrs): ...
    def handle_endtag(self, tag): ...
    def handle_data(self, data): ...
```
Handles all HTML edge cases correctly, including multi-line tags, entity decoding
via `convert_charrefs=True`, and case-insensitive tag names.

### 4.8  `html.unescape()` replaces hand-rolled decoder

The 60-line `html_unescape.py` (with its own Python 2/3 shims) is entirely
replaced by the stdlib one-liner:
```python
import html
text = html.unescape(raw_text)
```
`html.unescape()` has been in the standard library since Python 3.4 and handles
all numeric (`&#123;`, `&#xABC;`) and named (`&amp;`, `&nbsp;`) entities correctly.

---

## 5  robots.txt Compliance

`urllib.robotparser.RobotFileParser` checks every URL before fetching:

```python
rp = urllib.robotparser.RobotFileParser()
rp.set_url(f"{scheme}://{netloc}/robots.txt")
rp.read()
return rp.can_fetch(user_agent, url)
```

Results are cached per-host to avoid fetching `robots.txt` repeatedly.
Disabled with `--no-robots` (use responsibly).

---

## 6  Rate Limiting and Timeout

- Every request passes `timeout=config.request_timeout` to `urlopen`.
- `time.sleep(config.delay_between_requests)` enforces a minimum gap between
  consecutive requests (default: 1 second).
- A descriptive `User-Agent` header is sent on every request.

---

## 7  SQLite Improvements

| Old behaviour | New behaviour |
|---|---|
| No `UNIQUE` constraint | `UNIQUE(page, link)` |
| No indexes | `CREATE INDEX` on `page` and `link` columns |
| `INSERT INTO` (allows duplicates) | `INSERT OR IGNORE` |
| One `conn.commit()` per row | Single batch commit via `executemany` |
| Global `conn` at module level | `CrawlerDB` context manager |
| `text_factory = OptimizedUnicode` (removed in 3.13) | Default (`str`) |
| Only cursor returned | Full context manager owns both conn and cursor |

The `crawl_log` table tracks per-URL fetch status and timestamp, enabling
resumable crawls and audit trails.

---

## 8  `wordcount.py` Changes

| Old | New |
|---|---|
| `sys.argv` manual parsing | `argparse` with `--top`, `--min-count`, `--total` |
| Manual dict counting | `collections.Counter` |
| `open(f, 'rU')` (removed in 3.11) | `Path.read_text(encoding='latin-1')` |
| Dead `remove_preposition` function | Removed |
| Broken `top_words(-1, ...)` logic | Clean `top_n` / `min_count` separation |
| Hamlet-specific stopword list | Removed |

---

## 9  Test Suite

66 tests across 4 modules, all run with `pytest` and requiring no network access.

| Module | Tests | What's covered |
|---|---|---|
| `test_fetcher.py` | 14 | URL validation, HTTP success/errors, timeout, robots blocking, encoding |
| `test_parser.py` | 17 | Link extraction, relative URL resolution, entity decoding, scheme filtering |
| `test_storage.py` | 16 | Schema creation, indexes, insert/retrieve, deduplication, context manager, dump |
| `test_wordcount.py` | 19 | File parsing, word counting, top_n, min_count, edge cases |

All tests use `pytest`'s `tmp_path` fixture for filesystem isolation.
Network calls in fetcher tests are mocked via `unittest.mock.patch`.

---

## 10  Packaging (`pyproject.toml`)

```toml
[project]
name = "simple-crawler"
version = "2.0.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v"
```

`pip install -e .` makes `python -m crawler` and the `webcrawler.py` entry
point available without `PYTHONPATH` manipulation.
