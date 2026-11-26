import unittest
from src.hash_table import HashTable
from src.probing_table import ProbingTable
from src.shortener import Shortener
from src.server import table_page


class DisplayTests(unittest.TestCase):
    def test_chain_length_and_probe_count_are_visible(self):
        for factory, phrase in [(HashTable, "체인 길이 2"), (ProbingTable, "탐지 2회")]:
            with self.subTest(table=factory.__name__):
                app = Shortener(factory)
                for url in ("https://github.com", "https://docs.python.org/3/"):
                    app.shorten(url)
                self.assertIn(phrase, table_page(app, factory is ProbingTable))
