import unittest
from unittest.mock import patch, Mock
import os
import sys
import requests
import shutil

sys.path.append('..')
from get_page import get_page

class TestGetPage(unittest.TestCase):

    def setUp(self):
        self.test_dir = 'test_html'
        self.test_file = os.path.join(self.test_dir, 'test.html')
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('get_page.requests.get')
    def test_get_page_success(self, mock_get):
        # Configure the mock to return a successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><h1>Test</h1></body></html>'
        mock_response.raise_for_status = Mock() # No-op for success
        mock_get.return_value = mock_response

        url = 'http://example.com'
        result = get_page(url, self.test_file)
        
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r', encoding='latin-1') as f:
            content = f.read()
            self.assertEqual(content, '<html><body><h1>Test</h1></body></html>')
        mock_get.assert_called_once_with(url, timeout=10)

    def test_get_page_invalid_url(self):
        result = get_page('invalid-url', self.test_file)
        self.assertEqual(result, -1)
        self.assertFalse(os.path.exists(self.test_file))

    @patch('get_page.requests.get')
    def test_get_page_not_found(self, mock_get):
        # Configure the mock to simulate a 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_get.return_value = mock_response

        url = 'http://example.com/nonexistent'
        result = get_page(url, self.test_file)
        
        self.assertEqual(result, -1)
        self.assertFalse(os.path.exists(self.test_file))
        mock_get.assert_called_once_with(url, timeout=10)

if __name__ == '__main__':
    unittest.main()
