""" Tests for policy.py """
import unittest
import mock

from starttls_policy import policy

test_json = '{\
    "author": "Electronic Frontier Foundation",\
        "comment": "Sample policy configuration file",\
        "expires": 1404677353,\
        "timestamp": 1401093333,\
        "policies": {\
            ".valid.example-recipient.com": {\
                "min-tls-version": "TLSv1.1",\
                    "mode": "enforce",\
                    "mxs": [".valid.example-recipient.com"],\
                    "tls-report": "https://tls-rpt.example-recipient.org/api/report"\
            }\
        }\
    }'

class TestPolicy(unittest.TestCase):
    """Test Policy config
    """

    def test_basic(self):
        mock_open = mock.mock_open(read_data=test_json)
        conf = policy.Config()
        with mock.patch('starttls_policy.policy.io.open', mock_open):
            conf.load()
        self.assertEqual(conf.author, "Electronic Frontier Foundation")
        self.assertEqual(conf.policies, {'.valid.example-recipient.com': {
                'min-tls-version': 'TLSv1.1',
                'mode': 'enforce',
                'mxs': ['.valid.example-recipient.com'],
                'tls-report': 'https://tls-rpt.example-recipient.org/api/report',
            }})

if __name__ == '__main__':
    unittest.main()
