#!/usr/bin/env python

import unittest
import os
import json

from jsonschema import validate

ROOT_DIR, _ = os.path.split(os.path.dirname(os.path.abspath(__file__)))
POLICY_FILE = os.path.join(ROOT_DIR, "policy.json")
SCHEMA_FILE = os.path.join(ROOT_DIR, "schema", "policy-0.1.schema.json")

class TestPolicyList(unittest.TestCase):
    def setUp(self):
        with open(POLICY_FILE) as pf:
            self.policy = json.load(pf)
        with open(SCHEMA_FILE) as sf:
            self.schema = json.load(sf)

    def test_schema_valid(self):
        self.assertIsNone(validate(self.policy, self.schema))

    def test_links_ok(self):
        policy_list = self.policy["policies"]
        policy_aliases = self.policy["policy-aliases"]
        pinsets = self.policy["pinsets"]

        def _validate_actual_policy(pol):
            if "pin" in pol:
                self.assertIn(pol["pin"], pinsets)

        for pol_key in policy_list:
            pol = policy_list[pol_key]
            if "policy-alias" in pol:
                self.assertIn(pol["policy-alias"], policy_aliases)
            else:
                _validate_actual_policy(pol)

        for pol in policy_aliases:
            _validate_actual_policy(pol)


if __name__ == '__main__':
    unittest.main()
