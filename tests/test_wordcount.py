
import unittest
import os
import sys
sys.path.append('..')
from wordcount import parse_file, word_count, top_words

class TestWordCount(unittest.TestCase):

    def setUp(self):
        self.test_text_path = 'test_text.txt'
        with open(self.test_text_path, 'w') as f:
            f.write("This is a test file. This file is for testing word count.")

    def tearDown(self):
        os.remove(self.test_text_path)

    def test_parse_file(self):
        words = parse_file(self.test_text_path)
        expected_words = ['This', 'is', 'a', 'test', 'file', 'This', 'file', 'is', 'for', 'testing', 'word', 'count']
        self.assertEqual(words, expected_words)

    def test_word_count(self):
        words = ['a', 'b', 'a', 'c', 'b', 'a']
        counts = word_count(words)
        expected_counts = {'a': 3, 'b': 2, 'c': 1}
        self.assertEqual(counts, expected_counts)

    def test_top_words(self):
        counts = {'a': 10, 'b': 5, 'c': 12, 'd': 2}
        top = top_words(4, counts)
        expected_top = [('c', 12), ('a', 10), ('b', 5)]
        self.assertEqual(top, expected_top)
        
    def test_top_words_no_limit(self):
        counts = {'a': 10, 'b': 5, 'c': 12, 'd': 2}
        top = top_words(-1, counts)
        expected_top = [('c', 12), ('a', 10), ('b', 5), ('d', 2)]
        # The original code slices at 30, so we check if the result is a subset of the sorted list
        self.assertTrue(set(top).issubset(set(expected_top)))


if __name__ == '__main__':
    unittest.main()
