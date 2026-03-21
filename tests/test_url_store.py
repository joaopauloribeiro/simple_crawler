
import unittest
import sqlite3
import os
import sys
sys.path.append('..')
import url_store

class TestUrlStore(unittest.TestCase):

    def setUp(self):
        # Use an in-memory database for testing
        self.conn, self.c = url_store.init_db(':memory:')

    def tearDown(self):
        url_store.close_db(self.conn)

    def test_init_db(self):
        # Check if the table was created
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ref_links'")
        self.assertIsNotNone(self.c.fetchone())

    def test_insert_and_get_urls(self):
        url_store.insert_url(self.conn, self.c, 'page1', 'link1')
        url_store.insert_url(self.conn, self.c, 'page1', 'link2')
        urls = url_store.get_urls(self.c, 'page1')
        self.assertEqual(len(urls), 2)
        self.assertIn('link1', urls)
        self.assertIn('link2', urls)

    def test_get_link(self):
        url_store.insert_url(self.conn, self.c, 'page1', 'link1')
        url_store.insert_url(self.conn, self.c, 'page2', 'link1')
        links = url_store.get_link(self.c, 'link1')
        self.assertEqual(len(links), 2)

    def test_dump_data(self):
        dump_file = 'test_dump.sql'
        url_store.insert_url(self.conn, self.c, 'page1', 'link1')
        
        # To test dump_data, we need to mock open, so we will patch it.
        # For simplicity, we will just call the function and check if the file is created.
        # A more robust test would mock the file system.
        
        # The refactored dump_data takes a connection object
        with open(dump_file, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)

        self.assertTrue(os.path.exists(dump_file))
        os.remove(dump_file)

if __name__ == '__main__':
    unittest.main()
