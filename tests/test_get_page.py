
import unittest
import os
import sys
import http.server
import socketserver
import threading
sys.path.append('..')
from get_page import get_page

class TestGetPage(unittest.TestCase):
    PORT = 8000
    server = None
    thread = None

    @classmethod
    def setUpClass(cls):
        # Create a simple server
        handler = http.server.SimpleHTTPRequestHandler
        cls.server = socketserver.TCPServer(("", cls.PORT), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.test_dir = 'test_html'
        self.test_file = os.path.join(self.test_dir, 'test.html')
        os.makedirs(self.test_dir, exist_ok=True)
        # Create a dummy file to be served
        with open('index.html', 'w') as f:
            f.write('<html><body><h1>Test</h1></body></html>')


    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists('index.html'):
            os.remove('index.html')
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_get_page_success(self):
        url = f'http://localhost:{self.PORT}/'
        result = get_page(url, self.test_file)
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, '<html><body><h1>Test</h1></body></html>')

    def test_get_page_invalid_url(self):
        result = get_page('invalid-url', self.test_file)
        self.assertEqual(result, -1)
        self.assertFalse(os.path.exists(self.test_file))

    def test_get_page_not_found(self):
        url = f'http://localhost:{self.PORT}/nonexistent'
        result = get_page(url, self.test_file)
        self.assertEqual(result, -1)
        self.assertFalse(os.path.exists(self.test_file))

if __name__ == '__main__':
    unittest.main()
