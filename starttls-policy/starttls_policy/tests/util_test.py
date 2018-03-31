""" Tests for util.py """
import datetime
import os
import unittest

import pkg_resources

from starttls_policy import util

class TestEnforceUtil(unittest.TestCase):
    """ Unittests for "enforcer" functions."""

    def test_enforce_in(self):
        array = ["a", "b", "c", "d"]
        func = util.enforce_in(array)
        self.assertTrue(func("a"))
        self.assertFalse(func(["a"]))
        self.assertFalse(func("e"))
        self.assertFalse(func(0))

    def test_enforce_type(self):
        func = util.enforce_type(int)
        self.assertFalse(func("a"))
        self.assertTrue(func(0))

    def test_enforce_list(self):
        func = util.enforce_list(util.enforce_type(int))
        self.assertFalse(func(["a", 2]))
        self.assertTrue(func([0, 1]))

    def test_enforce_fields(self):
        func = util.enforce_fields(util.enforce_type(int))
        self.assertFalse(func({"b": "a", "c": 2}))
        self.assertTrue(func({"a": 0, "b": 1}))

    def test_enforce_disallow(self):
        self.assertFalse(util.enforce_disallow())

    def test_enforce_in_context(self):
        parent = {'field': ['a', 'b']}
        parent2 = {'field': {"a": 1, "b": 2}}
        func = util.enforce_in_context_field("field")
        self.assertTrue(func("a", parent))
        self.assertTrue(func("a", parent2))
        self.assertFalse(func("c", parent))
        self.assertFalse(func("c", parent2))

    def test_enforce_schema(self):
        mock_spec = {"a": util.enforce_type(int)}
        func = util.enforce_schema(mock_spec)
        self.assertTrue(func({"a": 0}))
        self.assertTrue(func({"b": 0}))
        self.assertFalse(func({"a": "b", "b": 0}))

    def test_enforce_schema_required(self):
        mock_spec = {"a": {'required': True}}
        func = util.enforce_schema(mock_spec)
        self.assertTrue(func({"a": 0}))
        self.assertFalse(func({"b": 0}))

    def test_enforce_schema_default(self):
        mock_spec = {"a": {'required': True, 'default': 0}}
        func = util.enforce_schema(mock_spec)
        obj = {"b": 0}
        self.assertTrue(func(obj))
        self.assertEqual(obj["a"], 0) # Default is set properly

    def test_enforce_schema_nested(self):
        nested_spec = {"a": util.enforce_type(int)}
        mock_spec = {"a": util.enforce_fields(util.enforce_schema(nested_spec))}
        func = util.enforce_schema(mock_spec)
        self.assertTrue(func({"a": {"A": {"a": 0}}}))
        self.assertFalse(func({"a": {"A": 0}}))
        self.assertTrue(func({"a": dict({})}))
        self.assertFalse(func({"a": {"A": {"a": "b"}}}))

class TestSchema(unittest.TestCase):
    """ Testing the schema definitions """

    def test_pins_valid(self):
        obj = {'expires': datetime.datetime.now(),
                'timestamp': datetime.datetime.now(),
                'pinsets': {'fake': dict({})},
                'policies': {
                    'mx.mail.com': {
                        'pin': 'fake',
                    }}}
        self.assertTrue(util.check_schema(obj, util.CONFIG_SCHEMA, error=False))
        obj.update({'pinsets': {'new_fake': dict({})}})
        self.assertFalse(util.check_schema(obj, util.CONFIG_SCHEMA, error=False))

    def test_aliases_valid(self):
        obj = {'expires': datetime.datetime.now(),
                'timestamp': datetime.datetime.now(),
                'policy-aliases': {'fake': dict({})},
                'policies': {
                    'mx.mail.com': {
                        'policy-alias': 'fake',
                    }}}
        self.assertTrue(util.check_schema(obj, util.CONFIG_SCHEMA, error=False))
        obj.update({'policy-aliases': {'new_fake': dict({})}})
        self.assertFalse(util.check_schema(obj, util.CONFIG_SCHEMA, error=False))

    def test_basic_parse_config(self):
        config_file = pkg_resources.resource_filename("starttls_policy.tests",
                          os.path.join("testdata", "config.json"))
        with open(config_file) as f:
            obj = util.deserialize_config(f.read())
        util.serialize_config(obj)

    def test_parse_actual_config(self):
        config_file = pkg_resources.resource_filename("starttls_policy", "policy.json")
        with open(config_file) as f:
            obj = util.deserialize_config(f.read())
        util.serialize_config(obj)

if __name__ == '__main__':
    unittest.main()
