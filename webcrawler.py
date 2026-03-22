import os
import time
from urllib.parse import quote_plus
import get_page
import find_links
from url_store import URLStore
import json

def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)

class Crawler:
    def __init__(self, seeds, db_name=None, download_folder=None):
        if db_name is None:
            config = get_config()
            db_name = config.get('crawler', {}).get('db_name', 'webcrawler.db')
        if download_folder is None:
            config = get_config()
            download_folder = config.get('crawler', {}).get('download_folder', 'html')

        self.seeds = seeds
        self.url_store = URLStore(db_name)
        self.download_folder = download_folder
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def get_filename(self, url):
        """Creates a valid filename from a URL."""
        # Use quote_plus to handle special characters in URLs
        # Replace / with _ to avoid creating subdirectories
        return os.path.join(self.download_folder, quote_plus(url).replace('/', '_') + '.html')

    def crawl(self, depth=1):
        urls_to_crawl = list(self.seeds)
        crawled_urls = set()
        
        for current_depth in range(depth + 1):
            next_urls_to_crawl = []
            for url in urls_to_crawl:
                if url in crawled_urls:
                    continue

                filename = self.get_filename(url)
                
                print(f"Crawling (depth {current_depth}): {url}")
                if get_page.get_page(url, filename) == -1:
                    crawled_urls.add(url) # Mark as crawled even if failed to avoid retries
                    continue

                crawled_urls.add(url)
                
                new_links = find_links.find_links(filename, url)
                
                for new_link, _ in new_links:
                    self.url_store.insert_url(url, new_link)
                    if new_link not in crawled_urls:
                        next_urls_to_crawl.append(new_link)
            
            urls_to_crawl = next_urls_to_crawl


def main():
    config = get_config()
    seeds = config.get('crawler', {}).get('seeds', [])
    
    crawler = Crawler(seeds)
    crawler.crawl(depth=1)

if __name__ == '__main__':
    main()
