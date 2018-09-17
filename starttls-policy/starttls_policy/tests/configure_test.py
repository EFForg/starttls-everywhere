""" Tests for configure.py """

import unittest

import json
import mock

from starttls_policy import configure

class MockGenerator(configure.ConfigGenerator):
    """Mock config generator for testing"""

    def _generate(self, policy_list):
        return "generated_config"

    def _instruct_string(self):
        return "instruct_string"

    @property
    def mta_name(self):
        return "fake"

    @property
    def default_filename(self):
        return "default_filename"

class TestConfigGenerator(unittest.TestCase):
    """Test the base config generator class"""
    def test_generate(self):
        generator = MockGenerator("./")
        with mock.patch("starttls_policy.configure.open", mock.mock_open()) as m:
            generator.generate()
            m().write.assert_any_call("generated_config")
            m().write.assert_any_call("\n")

    def test_manual_instructions(self):
        generator = MockGenerator("./")
        with mock.patch("starttls_policy.configure.six.print_") as mock_print:
            generator.manual_instructions()
            mock_print.assert_called_once_with("\n"
                "--------------------------------------------------\n"
                "Manual installation instructions for fake\n"
                "--------------------------------------------------\n"
                "instruct_string")


test_json = '{\
    "author": "Electronic Frontier Foundation",\
    "timestamp": "2018-06-18T09:41:50.264201364-07:00",\
    "expires": "2018-07-16T09:41:50.264201364-07:00",\
        "policies": {\
            ".valid.example-recipient.com": {\
                "mode": "enforce",\
                "mxs": [".valid.example-recipient.com"]\
            },\
            ".testing.example-recipient.com": {\
                "mode": "testing",\
                "mxs": [".testing.example-recipient.com"]\
            }\
        }\
    }'

class TestPostfixGenerator(unittest.TestCase):
    """Test Postfix config generator"""

    def test_generate(self):
        from starttls_policy import policy
        conf = policy.Config()
        conf.load_from_dict(json.loads(test_json))
        generator = configure.PostfixGenerator("./")
        result = generator._generate(conf) # pylint: disable=protected-access
        self.assertEqual(result, ".testing.example-recipient.com may \n"
                         ".valid.example-recipient.com    "
                         "secure match=.valid.example-recipient.com")

    def test_mta_name(self):
        generator = configure.PostfixGenerator("./")
        self.assertEqual(generator.mta_name, "Postfix")

    def test_instruct_string(self):
        generator = configure.PostfixGenerator("./")
        instructions = generator._instruct_string() # pylint: disable=protected-access
        self.assertTrue("postmap" in instructions)
        self.assertTrue("postconf -e \"smtp_tls_policy_maps=" in instructions)
        self.assertTrue("postfix reload" in instructions)
        self.assertTrue(generator.default_filename in instructions)

if __name__ == "__main__":
    unittest.main()
