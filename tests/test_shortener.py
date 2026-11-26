import unittest
from src.hash_table import HashTable
from src.shortener import Shortener


class ShortenerContract:
    factory = None

    def setUp(self):
        self.app = Shortener(self.factory)

    def test_reuse_and_reverse(self):
        a, b = "https://github.com", "https://docs.python.org/3/"
        self.assertEqual([self.app.shorten(url) for url in (a, b, a)], ["1", "2", "1"])
        self.assertEqual([self.app.resolve(code) for code in ("1", "2", "X")], [a, b, None])

    def test_rejected_input_does_not_take_a_code(self):
        for url in ["", " https://a.com", "https://a.com ", "https://a.com/a b", "https://a.com/\t",
                    "https://a.com/\u00a0", "ftp://a.com", "http:///x", "https://a.com:99999",
                    "https://a.com/" + "x" * 2048, "https://a.com/\x00"]:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    self.app.shorten(url)
        self.assertEqual(self.app.shorten("http://example.com"), "1")

    def test_length_limit(self):
        prefix = "https://example.com/"
        url = prefix + "z" * (2048 - len(prefix))
        self.assertEqual(self.app.resolve(self.app.shorten(url)), url)


class ChainingShortenerTests(ShortenerContract, unittest.TestCase):
    factory = HashTable
