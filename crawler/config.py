from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CrawlerConfig:
    seeds: list[str] = field(default_factory=lambda: [
        "https://news.ycombinator.com",
        "https://www.bbc.com/news",
        "https://www.reuters.com",
        "https://www.wikipedia.org",
        "https://techcrunch.com",
        "https://www.theguardian.com",
        "https://arstechnica.com",
        "https://www.nature.com/news",
    ])
    output_dir: Path = field(default_factory=lambda: Path("html"))
    db_path: Path = field(default_factory=lambda: Path("crawler.db"))
    request_timeout: int = 10
    delay_between_requests: float = 1.0
    user_agent: str = "SimpleCrawler/2.0 (Educational; +https://github.com/joaopauloribeiro/simple_crawler)"
    respect_robots: bool = True
    max_secondary_pages: int = 200
