import unittest
import os
import sys
sys.path.append('..')
from find_links import find_links

class TestFindLinks(unittest.TestCase):

    def setUp(self):
        self.test_html_path = 'test_page.html'

    def tearDown(self):
        if os.path.exists(self.test_html_path):
            os.remove(self.test_html_path)

    def test_find_links_with_links(self):
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
        base_url = 'http://example.com'
        links = find_links(self.test_html_path, base_url)
        self.assertEqual(len(links), 2)
        self.assertIn(('https://www.google.com', 'Google'), links)
        # Note: BeautifulSoup automatically handles HTML entities
        self.assertIn(('https://www.python.org', 'Python & stuff'), links)

    def test_find_links_relative_links(self):
        with open(self.test_html_path, 'w') as f:
            f.write("""
            <html>
            <body>
                <a href="/about">About</a>
                <a href="contact.html">Contact</a>
                <a href="../home">Home</a>
            </body>
            </html>
            """)
        base_url = 'http://example.com/info/company/'
        links = find_links(self.test_html_path, base_url)
        self.assertEqual(len(links), 3)
        self.assertIn(('http://example.com/about', 'About'), links)
        self.assertIn(('http://example.com/info/company/contact.html', 'Contact'), links)
        self.assertIn(('http://example.com/info/home', 'Home'), links)


    def test_find_links_no_links(self):
        with open(self.test_html_path, 'w') as f:
            f.write("<html><body><p>No links here</p></body></html>")
        base_url = 'http://example.com'
        links = find_links(self.test_html_path, base_url)
        self.assertEqual(len(links), 0)

    def test_find_links_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            find_links('non_existent_file.html', 'http://example.com')

if __name__ == '__main__':
    unittest.main()
