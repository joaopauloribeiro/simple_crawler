import unittest
from unittest.mock import patch, mock_open
import os
import sys
sys.path.append('..')
from url_store import URLStore

class TestUrlStore(unittest.TestCase):

    def setUp(self):
        # Use an in-memory database for testing
        self.url_store = URLStore(db_name=':memory:')

    def tearDown(self):
        self.url_store.close()

    def test_table_creation(self):
        # Check if the table was created
        self.url_store.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ref_links'")
        self.assertIsNotNone(self.url_store.c.fetchone())

    def test_insert_and_get_urls(self):
        self.url_store.insert_url('page1', 'link1')
        self.url_store.insert_url('page1', 'link2')
        urls = self.url_store.get_urls('page1')
        self.assertEqual(len(urls), 2)
        self.assertIn('link1', urls)
        self.assertIn('link2', urls)

    def test_get_link(self):
        self.url_store.insert_url('page1', 'link1')
        self.url_store.insert_url('page2', 'link1')
        pages = self.url_store.get_link('link1')
        self.assertEqual(len(pages), 2)
        self.assertIn('page1', pages)
        self.assertIn('page2', pages)

    @patch('builtins.open', new_callable=mock_open)
    def test_dump_data(self, mock_file):
        self.url_store.insert_url('page1', 'link1')
        self.url_store.dump_data('test_dump.sql')
        
        # Check that open was called with the correct file
        mock_file.assert_called_once_with('test_dump.sql', 'w')
        
        # Check that something was written to the file
        handle = mock_file()
        handle.write.assert_called()

if __name__ == '__main__':
    unittest.main()
