""" Tests for update.py """
import logging
import unittest
import mock

from starttls_policy import update

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TestUpdate(unittest.TestCase):
    """Test Configuration update tool
    """

    @mock.patch('starttls_policy.update._get_remote_data')
    def test_update_when_outdated(self, mock_get_remote_data):
        remote_data = '{ \"timestamp\": 1, \"expires\": 1 }'
        mock_get_remote_data.return_value = remote_data
        update_mock_open = mock.mock_open()
        with mock.patch('starttls_policy.update.open', update_mock_open):
            with mock.patch('starttls_policy.update.policy.io.open',
                            mock.mock_open(read_data="{\"timestamp\": 0, \"expires\": 0}")):
                update.update()
        self.assertTrue(update_mock_open.called, 'should have tried to update local file')
        update_mock_open().write.assert_called_once_with(remote_data)

    @mock.patch('starttls_policy.update._get_remote_data')
    def test_no_update_when_not_outdated(self, mock_get_remote_data):
        mock_get_remote_data.return_value = '{ \"timestamp\": 0, \"expires\": 0 }'
        update_mock_open = mock.mock_open()
        with mock.patch('starttls_policy.update.open', update_mock_open):
            with mock.patch('starttls_policy.update.policy.io.open',
                            mock.mock_open(read_data="{\"timestamp\": 0, \"expires\": 0}")):
                update.update()
        self.assertFalse(update_mock_open.called, 'should not have tried to update local file')

if __name__ == '__main__':
    unittest.main()
