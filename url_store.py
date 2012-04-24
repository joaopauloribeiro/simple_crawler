'''
Created on Apr 22, 2012

@author: lordzeus
'''

import sqlite3
import time
conn = sqlite3.connect('webcrawler.db')

def init_db():
	conn.text_factory = sqlite3.OptimizedUnicode
	c = conn.cursor()
	#c.execute('CREATE TABLE ref_links (page text, link text, date text)')
	c.execute('CREATE TABLE IF NOT EXISTS ref_links (page text, link text, date text)')
	return c

def insert_url(page, url, c):
	value = (page, url, time.asctime())
	c.execute("INSERT INTO ref_links VALUES (?,?,?)",value)
	conn.commit()

def get_link(link, c):
	query = (link,)
	c.execute("SELECT * FROM ref_links WHERE link = ?", query)
	result = []
	for row in c.fetchall():
		print(row)
		result.append(row[1])
	return result 

def get_urls(page, c):
	query = (page,)
	c.execute("SELECT * FROM ref_links WHERE page = ?", query)
	result = []
	for row in c.fetchall():
		print(row)
		result.append(row[1])
	return result 

def dump_data():
	with open('dump.sql', 'w') as f:
	    for line in conn.iterdump():
	        f.write('%s\n' % line)
	f.close()

def close_db(c):
	c.close()

if __name__ == '__main__':
	c = init_db()
	insert_url("http://www.google.com", "http://plus.google.com", c)
	insert_url("http://www.google.com", "http://image.google.com", c)
	insert_url("http://www.google.com", "http://reader.google.com", c)
	urls = get_urls("http://www.google.com", c)
	print(urls)
	close_db(c)
