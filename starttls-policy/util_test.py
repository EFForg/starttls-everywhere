import copy
import itertools
import logging
import unittest

import util

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TestUtil(unittest.TestCase):
    """Test Configuration utilities 
    """

    def test_basic_parse_config(self):
        with open("test_rules/config.json") as f:
            obj = util.deserialize_config(f.read())
        s = util.serialize_config(obj)

if __name__ == '__main__':
    unittest.main()
