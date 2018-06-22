""" Tests for main.py """
import unittest
import sys
import mock

from starttls_policy import main

class TestArguments(unittest.TestCase):
    def test_update_only_arg(self):
        sys.argv = ["_", "--update-only"]
        parser = main._argument_parser()
        args = parser.parse_args()
        self.assertTrue(args.update_only)

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
        sys.argv = ["_", "--update-only", "--policy-dir", "lmao"]
        parser = main._argument_parser()
        arguments = parser.parse_args()
        self.assertEqual(arguments.policy_dir, "lmao")

class TestPerform(unittest.TestCase):
    @mock.patch("starttls_policy.main._generate")
    @mock.patch("starttls_policy.main._update")
    def test_perform_update(self, update, generate):
        sys.argv = ["_", "--update-only"]
        parser = main._argument_parser()
        main._perform(parser.parse_args(), parser)
        update.assert_called_once()
        generate.assert_not_called()

    @mock.patch("starttls_policy.main._generate")
    @mock.patch("starttls_policy.main._update")
    def test_perform_generate(self, update, generate):
        main.GENERATORS = { "exists": mock.MagicMock() }
        sys.argv = ["_", "--generate", "exists"]
        parser = main._argument_parser()
        main._perform(parser.parse_args(), parser)
        generate.assert_called_once()
        update.assert_not_called()

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

    @mock.patch("starttls_policy.main._ensure_directory")
    @mock.patch("starttls_policy.main.update.update")
    def test_update(self, mock_update, ensure_directory):
        sys.argv = ["_", "--update-only"]
        parser = main._argument_parser()
        main._perform(parser.parse_args(), parser)
        mock_update.assert_called_once()

if __name__ == '__main__':
    unittest.main()
