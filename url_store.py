'''
Created on Apr 22, 2012

@author: lordzeus
'''

import sqlite3
import time


def init_db(db_name='webcrawler.db'):
    conn = sqlite3.connect(db_name)
    conn.text_factory = sqlite3.OptimizedUnicode
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS ref_links (page TEXT, link TEXT, date TEXT)')
    return conn, c


def insert_url(conn, c, page, url):
    value = (page, url, time.asctime())
    c.execute("INSERT INTO ref_links VALUES (?,?,?)", value)
    conn.commit()


def get_link(c, link):
    query = (link,)
    c.execute("SELECT * FROM ref_links WHERE link = ?", query)
    result = []
    for row in c.fetchall():
        print(row)
        result.append(row[1])
    return result


def get_urls(c, page):
    query = (page,)
    c.execute("SELECT * FROM ref_links WHERE page = ?", query)
    result = []
    for row in c.fetchall():
        print(row)
        result.append(row[1])
    return result


def dump_data(conn):
    with open('dump.sql', 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    f.close()


def close_db(conn):
    conn.close()


if __name__ == '__main__':
    conn, c = init_db()
    insert_url(conn, c, "http://www.google.com", "http://plus.google.com")
    insert_url(conn, c, "http://www.google.com", "http://image.google.com")
    insert_url(conn, c, "http://www.google.com", "http://reader.google.com")
    urls = get_urls(c, "http://www.google.com")
    print(urls)
    close_db(conn)
