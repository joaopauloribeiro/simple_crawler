"""
Web crawler entry point.

Usage:
    python webcrawler.py [--seeds URL ...] [--db PATH] [--timeout N]
                         [--delay SECS] [--max-pages N] [--no-robots]
                         [--dump-sql]
"""
import argparse
import logging
import time
from pathlib import Path

from crawler.config import CrawlerConfig
from crawler.fetcher import get_page
from crawler.parser import find_links
from crawler.storage import CrawlerDB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _safe_filename(url: str) -> str:
    return url.replace("://", "__").replace("/", "_").replace(".", "-")[:100] + ".html"


def crawl(config: CrawlerConfig) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)

    with CrawlerDB(config.db_path) as db:
        # ── Phase 1: fetch seeds, collect primary links ──────────────────
        primary: dict[str, str] = {}  # discovered_url -> seed that led to it

        for seed in config.seeds:
            seed_file = config.output_dir / _safe_filename(seed)
            ok = get_page(
                seed, seed_file,
                user_agent=config.user_agent,
                timeout=config.request_timeout,
                respect_robots=config.respect_robots,
            )
            db.log_crawl(seed, "ok" if ok else "failed")
            if not ok:
                continue
            for url, _ in find_links(seed_file, base_url=seed):
                primary.setdefault(url, seed)
            time.sleep(config.delay_between_requests)

        logger.info("Phase 1 complete — %d primary links found", len(primary))

        # ── Phase 2: fetch primary pages, collect secondary links ─────────
        secondary: dict[str, str] = {}  # discovered_url -> primary page that led to it

        for idx, (primary_url, _) in enumerate(primary.items()):
            if idx >= config.max_secondary_pages:
                logger.info("Secondary page cap (%d) reached", config.max_secondary_pages)
                break
            page_file = config.output_dir / f"p2_{idx:05d}.html"
            ok = get_page(
                primary_url, page_file,
                user_agent=config.user_agent,
                timeout=config.request_timeout,
                respect_robots=config.respect_robots,
            )
            db.log_crawl(primary_url, "ok" if ok else "failed")
            if not ok:
                continue
            for url, _ in find_links(page_file, base_url=primary_url):
                if url not in primary:
                    secondary.setdefault(url, primary_url)
            time.sleep(config.delay_between_requests)

        logger.info("Phase 2 complete — %d secondary links found", len(secondary))

        # ── Persist ───────────────────────────────────────────────────────
        pairs = (
            [(src, url) for url, src in primary.items()] +
            [(src, url) for url, src in secondary.items()]
        )
        inserted = db.insert_links_batch(pairs)
        logger.info(
            "Done. %d new records stored. Total in DB: %d",
            inserted, db.total_links(),
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple educational web crawler",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--seeds", nargs="+", metavar="URL",
                        help="Seed URLs (overrides built-in list)")
    parser.add_argument("--db", default="crawler.db", metavar="PATH",
                        help="SQLite database path")
    parser.add_argument("--timeout", type=int, default=10, metavar="N",
                        help="Per-request timeout in seconds")
    parser.add_argument("--delay", type=float, default=1.0, metavar="SECS",
                        help="Seconds to wait between requests")
    parser.add_argument("--max-pages", type=int, default=200, metavar="N",
                        help="Max secondary pages to crawl")
    parser.add_argument("--no-robots", action="store_true",
                        help="Ignore robots.txt (use responsibly)")
    parser.add_argument("--dump-sql", action="store_true",
                        help="Dump database to dump.sql after crawling")
    args = parser.parse_args()

    defaults = CrawlerConfig()
    config = CrawlerConfig(
        seeds=args.seeds or defaults.seeds,
        db_path=Path(args.db),
        request_timeout=args.timeout,
        delay_between_requests=args.delay,
        max_secondary_pages=args.max_pages,
        respect_robots=not args.no_robots,
    )

    crawl(config)

    if args.dump_sql:
        with CrawlerDB(config.db_path) as db:
            db.dump_sql()


if __name__ == "__main__":
    main()
