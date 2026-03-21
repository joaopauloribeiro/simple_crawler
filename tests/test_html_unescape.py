
import unittest
import sys
sys.path.append('..')
from html_unescape import unescape

class TestHtmlUnescape(unittest.TestCase):

    def test_unescape_common_entities(self):
        self.assertEqual(unescape('&amp; &lt; &gt;'), '& < >')

    def test_unescape_numerical_entities(self):
        self.assertEqual(unescape('&#34; &#x22;'), '" "')

    def test_unescape_no_entities(self):
        self.assertEqual(unescape('Hello world'), 'Hello world')

    def test_unescape_invalid_entities(self):
        self.assertEqual(unescape('&invalid;'), '&invalid;')
        
    def test_mixed_entities(self):
        self.assertEqual(unescape('Hello &amp; world &#34;'), 'Hello & world "')

if __name__ == '__main__':
    unittest.main()
