""" Tests for main.py """
import unittest
import sys
import mock

from starttls_policy import main

class TestArguments(unittest.TestCase):
    def test_no_args_require_generate(self):
        sys.argv = ["_"]
        parser = main._argument_parser()
        parser.error = mock.MagicMock(side_effect=Exception)
        self.assertRaises(Exception, parser.parse_args)

    def test_generate_no_arg(self):
        sys.argv = ["_", "--generate"]
        parser = main._argument_parser()
        parser.error = mock.MagicMock(side_effect=Exception)
        self.assertRaises(Exception, parser.parse_args)

    def test_generate_arg(self):
        sys.argv = ["_", "--generate", "lol"]
        parser = main._argument_parser()
        arguments = parser.parse_args()
        self.assertEqual(arguments.generate, "lol")

    def test_default_dir(self):
        sys.argv = ["_", "--generate", "lol"]
        parser = main._argument_parser()
        arguments = parser.parse_args()
        self.assertEqual(arguments.policy_dir, "/etc/starttls-policy/")

    def test_policy_dir(self):
        sys.argv = ["_", "--generate", "lol", "--policy-dir", "lmao"]
        parser = main._argument_parser()
        arguments = parser.parse_args()
        self.assertEqual(arguments.policy_dir, "lmao")

class TestPerform(unittest.TestCase):
    def test_generate_unknown(self):
        sys.argv = ["_", "--generate", "lmao"]
        parser = main._argument_parser()
        parser.error = mock.MagicMock(side_effect=Exception)
        self.assertRaises(Exception, main._perform, parser.parse_args(), parser)

    @mock.patch("starttls_policy.main._ensure_directory")
    def test_generate(self, ensure_directory):
        main.GENERATORS = { "exists": mock.MagicMock() }
        sys.argv = ["_", "--generate", "exists"]
        parser = main._argument_parser()
        main._perform(parser.parse_args(), parser)
        self.assertTrue(main.GENERATORS["exists"].called_with("/etc/starttls-policy"))

if __name__ == '__main__':
    unittest.main()
