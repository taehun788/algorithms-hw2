import unittest
from src.base62 import encode, decode


class Base62Tests(unittest.TestCase):
    def test_alphabet_and_boundaries(self):
        for number, code in [(0, "0"), (10, "a"), (35, "z"), (36, "A"), (61, "Z"), (62, "10")]:
            self.assertEqual(encode(number), code)
            self.assertEqual(decode(code), number)

    def test_round_trip(self):
        for number in [1, 62**2 - 1, 62**8 + 37]:
            self.assertEqual(decode(encode(number)), number)

    def test_invalid(self):
        for value in [-1, True, 1.5]:
            with self.assertRaises(ValueError):
                encode(value)
        for value in ["", "-1", "é", None]:
            with self.assertRaises(ValueError):
                decode(value)
