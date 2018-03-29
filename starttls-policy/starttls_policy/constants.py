""" Constants. """

import os

POLICY_REMOTE_URL = "https://raw.githubusercontent.com/sydneyli/starttls-everywhere/policy.json"
POLICY_FILENAME = "policy.json"
POLICY_LOCAL_FILE = os.path.join(os.path.dirname(__file__), POLICY_FILENAME)
