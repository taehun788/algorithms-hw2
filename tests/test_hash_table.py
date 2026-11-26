import unittest
from src.hash_table import HashTable, horner


class TableContract:
    factory = None

    def setUp(self):
        self.table = self.factory(16, max_load=None)

    def test_actual_collision(self):
        a, b = "https://github.com", "https://docs.python.org/3/"
        self.assertEqual([horner(u, 16) for u in (a, b)], [5, 5])
        self.table.put(a, "1")
        self.table.put(b, "2")
        self.assertEqual((self.table.get(a), self.table.get(b)), ("1", "2"))
        self.assertEqual(len(self.table), 2)

    def test_update(self):
        self.table.put("hello", "1")
        self.table.put("hello", "2")
        self.assertEqual(len(self.table), 1)
        self.assertEqual(self.table.get("hello"), "2")
        self.assertIn("hello", self.table)
        self.assertNotIn("world", self.table)
        self.assertIsNone(self.table.get("world"))
        self.assertAlmostEqual(self.table.load_factor, 1 / 16)

    def test_resize_keeps_keys(self):
        table = self.factory(2)
        for i in range(30):
            table.put(str(i), str(i + 1))
        self.assertGreater(table.capacity, 2)
        self.assertEqual([table.get(str(i)) for i in range(30)], [str(i + 1) for i in range(30)])


class ChainingTests(TableContract, unittest.TestCase):
    factory = HashTable

    def test_counts(self):
        table = self.factory(1, max_load=None)
        self.assertEqual(table.find("absent"), (None, 0))
        table.put("a", "1")
        table.put("b", "2")
        self.assertEqual(table.find("b"), ("2", 1))
        self.assertEqual(table.find("a"), ("1", 2))
        self.assertEqual(table.find("none"), (None, 2))
