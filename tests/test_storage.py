"""Tests for crawler.storage."""
import pytest

from crawler.storage import CrawlerDB


@pytest.fixture
def db(tmp_path):
    with CrawlerDB(tmp_path / "test.db") as database:
        yield database


class TestCrawlerDBInit:
    def test_creates_ref_links_table(self, db):
        cur = db._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ref_links'"
        )
        assert cur.fetchone() is not None

    def test_creates_crawl_log_table(self, db):
        cur = db._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='crawl_log'"
        )
        assert cur.fetchone() is not None

    def test_creates_index_on_page(self, db):
        cur = db._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_ref_page'"
        )
        assert cur.fetchone() is not None

    def test_creates_index_on_link(self, db):
        cur = db._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_ref_link'"
        )
        assert cur.fetchone() is not None


class TestInsertAndRetrieve:
    def test_insert_and_get_links_from(self, db):
        db.insert_links_batch([("http://source.com", "http://target.com")])
        assert "http://target.com" in db.get_links_from("http://source.com")

    def test_insert_and_get_pages_linking_to(self, db):
        db.insert_links_batch([
            ("http://a.com", "http://target.com"),
            ("http://b.com", "http://target.com"),
        ])
        pages = db.get_pages_linking_to("http://target.com")
        assert "http://a.com" in pages
        assert "http://b.com" in pages

    def test_batch_insert_100_rows(self, db):
        pairs = [(f"http://src{i}.com", f"http://dst{i}.com") for i in range(100)]
        db.insert_links_batch(pairs)
        assert db.total_links() == 100

    def test_total_links_returns_correct_count(self, db):
        assert db.total_links() == 0
        db.insert_links_batch([("http://a.com", "http://b.com")])
        assert db.total_links() == 1

    def test_get_links_from_unknown_page_returns_empty(self, db):
        assert db.get_links_from("http://nobody.com") == []


class TestDeduplication:
    def test_duplicate_pair_inserted_once(self, db):
        pair = [("http://source.com", "http://target.com")]
        db.insert_links_batch(pair)
        db.insert_links_batch(pair)
        assert db.get_links_from("http://source.com").count("http://target.com") == 1

    def test_same_link_different_pages_both_stored(self, db):
        db.insert_links_batch([
            ("http://page1.com", "http://shared.com"),
            ("http://page2.com", "http://shared.com"),
        ])
        pages = db.get_pages_linking_to("http://shared.com")
        assert len(pages) == 2


class TestCrawlLog:
    def test_log_crawl_stores_status(self, db):
        db.log_crawl("http://example.com", "ok")
        cur = db._conn.execute(
            "SELECT status FROM crawl_log WHERE url=?", ("http://example.com",)
        )
        assert cur.fetchone()[0] == "ok"

    def test_log_crawl_replaces_previous_entry(self, db):
        db.log_crawl("http://example.com", "failed")
        db.log_crawl("http://example.com", "ok")
        cur = db._conn.execute(
            "SELECT status FROM crawl_log WHERE url=?", ("http://example.com",)
        )
        assert cur.fetchone()[0] == "ok"


class TestContextManager:
    def test_connection_closed_after_with_block(self, tmp_path):
        with CrawlerDB(tmp_path / "test.db") as database:
            assert database._conn is not None
        assert database._conn is None

    def test_can_reopen_same_database(self, tmp_path):
        db_path = tmp_path / "test.db"
        with CrawlerDB(db_path) as db1:
            db1.insert_links_batch([("http://a.com", "http://b.com")])
        with CrawlerDB(db_path) as db2:
            assert db2.total_links() == 1


class TestDumpSQL:
    def test_dump_creates_file(self, db, tmp_path):
        db.insert_links_batch([("http://a.com", "http://b.com")])
        out = tmp_path / "dump.sql"
        db.dump_sql(out)
        assert out.exists()

    def test_dump_contains_table_name(self, db, tmp_path):
        out = tmp_path / "dump.sql"
        db.dump_sql(out)
        assert "ref_links" in out.read_text()
