'''
Created on Apr 22, 2012

@author: lordzeus
'''

import sqlite3
import time

conn = sqlite3.connect('teste.db')

conn.text_factory = sqlite3.OptimizedUnicode

c = conn.cursor()

#create table
c.execute('CREATE TABLE ref_links (page text, link text, date text)')
value = ('http://www.about.com', 'http://www.nytco.com', time.asctime())

c.execute("INSERT INTO ref_links VALUES (?,?,?)",value)
conn.commit()

c.execute("SELECT * FROM ref_links")
print c.fetchone()

with open('dump.sql', 'w') as f:
    for line in conn.iterdump():
        f.write('%s\n' % line)
f.close()

conn3 = sqlite3.connect("replica.db")

conn3.text_factory = sqlite3.OptimizedUnicode

dump = open('dump.sql','r')

script = dump.read()

c3 = conn3.cursor()

c3.executescript(script)

c3.execute("SELECT * FROM ref_links")

print c3.fetchone()

dump.close()
c3.close()
c.close()
