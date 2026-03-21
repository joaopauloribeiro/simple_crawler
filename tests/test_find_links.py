
import unittest
import os
import sys
sys.path.append('..')
from find_links import find_links

class TestFindLinks(unittest.TestCase):

    def setUp(self):
        self.test_html_path = 'test_page.html'
        with open(self.test_html_path, 'w') as f:
            f.write("""
            <html>
            <body>
                <a href="https://www.google.com">Google</a>
                <a href="https://www.python.org">Python &amp; stuff</a>
                <a href="#internal">Internal link</a>
            </body>
            </html>
            """)

    def tearDown(self):
        os.remove(self.test_html_path)

    def test_find_links_with_links(self):
        links = find_links(self.test_html_path)
        self.assertEqual(len(links), 2)
        self.assertIn(('https://www.google.com', 'Google'), links)
        self.assertIn(('https://www.python.org', 'Python & stuff'), links)

    def test_find_links_no_links(self):
        with open(self.test_html_path, 'w') as f:
            f.write("<html><body><p>No links here</p></body></html>")
        links = find_links(self.test_html_path)
        self.assertEqual(len(links), 0)

    def test_find_links_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            find_links('non_existent_file.html')

if __name__ == '__main__':
    unittest.main()
