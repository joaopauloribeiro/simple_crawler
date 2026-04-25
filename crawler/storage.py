import logging
import sqlite3
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS ref_links (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    page    TEXT    NOT NULL,
    link    TEXT    NOT NULL,
    date    TEXT    NOT NULL,
    UNIQUE(page, link)
);
CREATE INDEX IF NOT EXISTS idx_ref_page ON ref_links(page);
CREATE INDEX IF NOT EXISTS idx_ref_link ON ref_links(link);

CREATE TABLE IF NOT EXISTS crawl_log (
    url        TEXT PRIMARY KEY,
    fetched_at TEXT NOT NULL,
    status     TEXT NOT NULL
);
"""


class CrawlerDB:
    def __init__(self, db_path: Path | str = "crawler.db") -> None:
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "CrawlerDB":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def insert_links_batch(self, pairs: list[tuple[str, str]]) -> int:
        """Insert (page, link) pairs, silently ignoring duplicates. Returns rows inserted."""
        assert self._conn is not None
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        rows = [(page, link, now) for page, link in pairs]
        cur = self._conn.executemany(
            "INSERT OR IGNORE INTO ref_links(page, link, date) VALUES (?, ?, ?)",
            rows,
        )
        self._conn.commit()
        return cur.rowcount

    def log_crawl(self, url: str, status: str) -> None:
        assert self._conn is not None
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._conn.execute(
            "INSERT OR REPLACE INTO crawl_log(url, fetched_at, status) VALUES (?, ?, ?)",
            (url, now, status),
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_links_from(self, page: str) -> list[str]:
        assert self._conn is not None
        cur = self._conn.execute(
            "SELECT link FROM ref_links WHERE page = ?", (page,)
        )
        return [row["link"] for row in cur.fetchall()]

    def get_pages_linking_to(self, link: str) -> list[str]:
        assert self._conn is not None
        cur = self._conn.execute(
            "SELECT page FROM ref_links WHERE link = ?", (link,)
        )
        return [row["page"] for row in cur.fetchall()]

    def total_links(self) -> int:
        assert self._conn is not None
        return self._conn.execute("SELECT COUNT(*) FROM ref_links").fetchone()[0]

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def dump_sql(self, output_path: Path | str = "dump.sql") -> None:
        assert self._conn is not None
        output_path = Path(output_path)
        with output_path.open("w", encoding="utf-8") as f:
            for line in self._conn.iterdump():
                f.write(f"{line}\n")
        logger.info("Database dumped to %s", output_path)
