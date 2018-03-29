""" Tests for update.py """
import datetime
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
    @mock.patch('starttls_policy.update.util.config_from_file')
    def test_update_when_outdated(self, mock_config_from_file, mock_get_remote_data):
        remote_data = '{ \"timestamp\": 1, \"expires\": 1 }'
        mock_get_remote_data.return_value = remote_data
        mock_config_from_file.return_value = {'timestamp': datetime.datetime.fromtimestamp(0)}
        mock_open = mock.mock_open()
        with mock.patch('starttls_policy.update.open', mock_open):
            update.update()
        self.assertTrue(mock_open.called, 'should have tried to update local file')
        mock_open().write.assert_called_once_with(remote_data)

    @mock.patch('starttls_policy.update._get_remote_data')
    @mock.patch('starttls_policy.update.util.config_from_file')
    def test_no_update_when_not_outdated(self, mock_config_from_file, mock_get_remote_data):
        mock_get_remote_data.return_value = '{ \"timestamp\": 0, \"expires\": 0 }'
        mock_config_from_file.return_value = {'timestamp': datetime.datetime.utcfromtimestamp(0)}
        mock_open = mock.mock_open()
        with mock.patch('starttls_policy.update.open', mock_open):
            update.update()
        self.assertFalse(mock_open.called, 'should not have tried to update local file')

if __name__ == '__main__':
    unittest.main()
