import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import tempfile
sys.path.append('..')
from webcrawler import Crawler

class TestWebCrawler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.download_folder = os.path.join(self.temp_dir.name, 'html')
        os.makedirs(self.download_folder)

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('webcrawler.URLStore')
    @patch('webcrawler.find_links.find_links')
    @patch('webcrawler.get_page.get_page')
    def test_crawler_logic_depth_0(self, mock_get_page, mock_find_links, mock_url_store_class):
        # Arrange
        seeds = ['http://example.com/page1', 'http://example.com/page2']
        mock_url_store_instance = MagicMock()
        mock_url_store_class.return_value = mock_url_store_instance
        mock_find_links.return_value = [('http://example.com/some_link', 'Some Link')]
        mock_get_page.return_value = 0

        # Act
        crawler = Crawler(seeds, download_folder=self.download_folder)
        crawler.crawl(depth=0)

        # Assert
        self.assertEqual(mock_get_page.call_count, 2)
        self.assertEqual(mock_find_links.call_count, 2)
        self.assertEqual(mock_url_store_instance.insert_url.call_count, 2)

    @patch('webcrawler.URLStore')
    @patch('webcrawler.find_links.find_links')
    @patch('webcrawler.get_page.get_page')
    def test_crawler_logic_depth_1(self, mock_get_page, mock_find_links, mock_url_store_class):
        # Arrange
        seeds = ['http://example.com/page1', 'http://example.com/page2']
        
        mock_url_store_instance = MagicMock()
        mock_url_store_class.return_value = mock_url_store_instance

        def find_links_side_effect(filename, base_url):
            if base_url == 'http://example.com/page1':
                return [('http://example.com/page3', 'Page 3')]
            if base_url == 'http://example.com/page2':
                return [('http://example.com/page4', 'Page 4')]
            if base_url == 'http://example.com/page3':
                return [('http://example.com/page5', 'Page 5')]
            return []
        mock_find_links.side_effect = find_links_side_effect
        mock_get_page.return_value = 0

        # Act
        crawler = Crawler(seeds, download_folder=self.download_folder)
        crawler.crawl(depth=1)

        # Assert
        self.assertEqual(mock_get_page.call_count, 4)
        self.assertEqual(mock_find_links.call_count, 4)
        self.assertEqual(mock_url_store_instance.insert_url.call_count, 3)
        expected_insert_calls = [
            call('http://example.com/page1', 'http://example.com/page3'),
            call('http://example.com/page2', 'http://example.com/page4'),
            call('http://example.com/page3', 'http://example.com/page5'),
        ]
        mock_url_store_instance.insert_url.assert_has_calls(expected_insert_calls, any_order=True)

if __name__ == '__main__':
    unittest.main()
