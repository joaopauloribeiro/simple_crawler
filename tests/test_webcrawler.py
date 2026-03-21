
import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append('..')
import webcrawler

class TestWebCrawler(unittest.TestCase):

    @patch('webcrawler.url_store')
    @patch('webcrawler.find_links')
    @patch('webcrawler.get_page')
    def test_main_crawler_logic(self, mock_get_page, mock_find_links, mock_url_store):
        # Arrange
        # Mock get_page to simulate successful page downloads
        mock_get_page.get_page.return_value = 0

        # Mock find_links to return different links for different pages
        def find_links_side_effect(filename):
            if 'opovo' in filename:
                return [('http://link1.com', 'Link 1')]
            if 'globo' in filename:
                return [('http://link2.com', 'Link 2')]
            if 'link1' in filename:
                return [('http://secondary-link.com', 'Secondary')]
            return []
        mock_find_links.find_links.side_effect = find_links_side_effect

        # Mock the url_store to avoid database interactions
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_url_store.init_db.return_value = (mock_conn, mock_cursor)

        # Act
        webcrawler.main()

        # Assert
        # Check that get_page was called for seeds and primary links
        self.assertIn(unittest.mock.call('http://www.opovo.com.br', 'html/opovo.html'), mock_get_page.get_page.call_args_list)
        self.assertIn(unittest.mock.call('http://www.globo.com', 'html/globo.html'), mock_get_page.get_page.call_args_list)
        self.assertIn(unittest.mock.call('http://link1.com', unittest.mock.ANY), mock_get_page.get_page.call_args_list)
        
        # Check that find_links was called
        mock_find_links.find_links.assert_any_call('html/opovo.html')
        mock_find_links.find_links.assert_any_call('html/globo.html')

        # Check that insert_url was called for the found links
        mock_url_store.insert_url.assert_any_call(mock_conn, mock_cursor, 'http://www.opovo.com.br', 'http://link1.com')
        mock_url_store.insert_url.assert_any_call(mock_conn, mock_cursor, 'http://www.globo.com', 'http://link2.com')
        mock_url_store.insert_url.assert_any_call(mock_conn, mock_cursor, 'http://link1.com', 'http://secondary-link.com')

        # Check that the database connection was closed
        mock_url_store.close_db.assert_called_once_with(mock_conn)

if __name__ == '__main__':
    unittest.main()
