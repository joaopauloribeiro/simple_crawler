import sqlite3
import time
import json

def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)

class URLStore:
    def __init__(self, db_name=None):
        if db_name is None:
            config = get_config()
            db_name = config.get('crawler', {}).get('db_name', 'webcrawler.db')
        
        self.conn = sqlite3.connect(db_name)
        self.conn.text_factory = sqlite3.OptimizedUnicode
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS ref_links (page TEXT, link TEXT, date TEXT)')

    def insert_url(self, page, url):
        value = (page, url, time.asctime())
        self.c.execute("INSERT INTO ref_links VALUES (?,?,?)", value)
        self.conn.commit()

    def get_link(self, link):
        query = (link,)
        self.c.execute("SELECT * FROM ref_links WHERE link = ?", query)
        result = []
        for row in self.c.fetchall():
            result.append(row[0]) # return the page where the link was found
        return result

    def get_urls(self, page):
        query = (page,)
        self.c.execute("SELECT * FROM ref_links WHERE page = ?", query)
        result = []
        for row in self.c.fetchall():
            result.append(row[1]) # return the link
        return result

    def dump_data(self, dump_file='dump.sql'):
        with open(dump_file, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()

if __name__ == '__main__':
    # Example usage:
    url_store = URLStore(db_name=':memory:')
    url_store.insert_url("http://www.google.com", "http://plus.google.com")
    url_store.insert_url("http://www.google.com", "http://image.google.com")
    url_store.insert_url("http://www.google.com", "http://reader.google.com")
    
    urls = url_store.get_urls("http://www.google.com")
    print("URLs found on http://www.google.com:", urls)
    
    pages = url_store.get_link("http://plus.google.com")
    print("Pages containing http://plus.google.com:", pages)
    
    # The connection will be closed automatically when the object is destroyed,
    # but it's good practice to close it explicitly.
    url_store.close()
