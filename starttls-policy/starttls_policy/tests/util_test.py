""" Tests for util.py """
import unittest
from functools import partial

from starttls_policy import util

class TestEnforceUtil(unittest.TestCase):
    """ Unittests for "enforcer" functions."""

    def test_enforce_in(self):
        array = ["a", "b", "c", "d"]
        func = partial(util.enforce_in, array)
        self.assertEqual(func("a"), "a")
        with self.assertRaises(util.ConfigError):
            func(["a"])
        with self.assertRaises(util.ConfigError):
            func("e")
        with self.assertRaises(util.ConfigError):
            func(0)

    def test_enforce_type(self):
        func = partial(util.enforce_type, int)
        with self.assertRaises(util.ConfigError):
            func("a")
        self.assertEqual(func(1), 1)

    def test_enforce_list(self):
        func = partial(util.enforce_list, partial(util.enforce_type, int))
        with self.assertRaises(util.ConfigError):
            func(["a", 2])
        self.assertEqual(func([0, 1]), [0, 1])

    def test_enforce_fields(self):
        func = partial(util.enforce_fields, partial(util.enforce_type, int))
        self.assertEqual(func({"a": 0, "b": 1}), {"a": 0, "b": 1})

    def test_enforce_bad_fields(self):
        func = partial(util.enforce_fields, partial(util.enforce_type, int))
        self.assertRaises(util.ConfigError, func, {"b": "a", "c": 2})

    def test_parse_bad_datestring(self):
        self.assertRaises(util.ConfigError, util.parse_valid_date, "fake")

if __name__ == '__main__':
    unittest.main()
