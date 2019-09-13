#!/usr/bin/env python

import unittest
import os
import json

from jsonschema import validate
import subprocess
import tempfile

ROOT_DIR, _ = os.path.split(os.path.dirname(os.path.abspath(__file__)))
POLICY_FILE = os.path.join(ROOT_DIR, "policy.json")
SCHEMA_FILE = os.path.join(ROOT_DIR, "schema", "policy-0.1.schema.json")

def _git_exists():
    try:
        subprocess.check_call(["git", "--version"])
    except subprocess.CalledProcessError as e:
        return False
    return True

def _policies_equal(policy1, policy2):
    return policy1['mode'] == policy2['mode'] and \
        tuple(sorted(policy1['mxs'])) == tuple(sorted(policy2['mxs']))

def _policy_lookup(policy_json, name):
    policies = policy_json['policies']
    if name not in policies:
        return None
    entry = policies[name]
    if "policy-alias" in entry:
        return policy_json["policy-aliases"][entry["policy-alias"]]
    return entry

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

        for pol_key in policy_list:
            pol = policy_list[pol_key]
            if "policy-alias" in pol:
                self.assertIn(pol["policy-alias"], policy_aliases)


    @unittest.skipIf("policy-update" in os.environ.get("TRAVIS_BRANCH", "") or not _git_exists(), "")
    def test_continuity(self):
        # if not on a policy-update branch, make sure that all the policies are functionally equivalent to before.
        # on policy-update branch: return
        proc = subprocess.Popen(["git","show","master:policy.json"], stdout=subprocess.PIPE)
        old_policy_raw = proc.stdout.read()
        with open("policy.json") as f:
            new_policy_raw = f.read()
        if len(old_policy_raw) == len(new_policy_raw) and old_policy_raw == new_policy_raw:
            return
        old_policy = json.loads(old_policy_raw)
        new_policy = json.loads(new_policy_raw)
        self.assertEqual(new_policy['policies'].keys(), old_policy['policies'].keys())
        for domain in new_policy['policies'].keys():
            self.assertTrue(_policies_equal(_policy_lookup(old_policy, domain), _policy_lookup(new_policy, domain)))


if __name__ == '__main__':
    unittest.main()
