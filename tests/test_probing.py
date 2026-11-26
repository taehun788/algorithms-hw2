import unittest
from src.probing_table import ProbingTable
from test_hash_table import TableContract
from test_shortener import ShortenerContract
from test_http import HttpContract


class ProbingTests(TableContract, unittest.TestCase):
    factory = ProbingTable

    def test_wrap_full_miss_and_update(self):
        table = self.factory(4, max_load=None)
        for key in "c g k o".split():  # 99, 103, 107, 111 all hash to 3 modulo 4
            table.put(key, key.upper())
        self.assertEqual(table.find("g"), ("G", 2))
        self.assertEqual(table.find("z"), (None, 4))
        self.assertEqual([x[1] for x in table.entries()], ["g", "k", "o", "c"])
        with self.assertRaises(OverflowError):
            table.put("s", "new")
        table.put("g", "replacement")
        self.assertEqual(table.get("g"), "replacement")
        self.assertEqual(len(table), 4)

    def test_empty_slot_costs_one(self):
        self.assertEqual(self.table.find("x"), (None, 1))


class ProbingShortenerTests(ShortenerContract, unittest.TestCase):
    factory = ProbingTable


class ProbingHttpTests(HttpContract, unittest.TestCase):
    factory = ProbingTable
    probing = True
