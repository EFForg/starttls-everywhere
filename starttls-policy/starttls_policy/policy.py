""" Policy config wrapper """
import logging
import io
from starttls_policy import util
from starttls_policy import constants

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

class Policy(object):
    """Class containing a single TLS policy information for a particular e-mail domain.
    """
    def __init__(self, data):
        self._data = data

    @property
    def min_tls_version(self):
        """ Getter for this policy's minimum TLS version.
        :returns str: """
        return self._data.get('min-tls-version', None)

    @property
    def mode(self):
        """ Getter for this policy's TLS mode.
        :returns str: """
        return self._data.get('mode', None)

    @property
    def mxs(self):
        """ Getter for the mx hosts that this domain's certs can be valid for.
        :returns list: """
        return self._data.get('mxs', [])

    @property
    def tls_report(self):
        """ Getter for the tls reporting endpoint for this policy
        :returns list: """
        return self._data.get('tls_report', [])

    @property
    def pin(self):
        """ Getter for the pinned keys for this policy
        :returns list: """
        return self._data.get('pin', [])

    @property
    def mta_sts(self):
        """ Getter for whether this policy supports MTA STS.
        :returns bool: """
        return self._data.get('mta-sts', False)

    @property
    def alias(self):
        """ Getter for this policy's alias, if it exists.
        :returns str: """
        return self._data.get('policy-alias', None)

class Config(object):
    """Class for retrieving properties in TLS Policy config.
    """
    def __init__(self, filename=constants.POLICY_LOCAL_FILE):
        self.filename = filename
        self._data = None

    def load(self):
        """Loads JSON configuration from file specified by `filename` property.
        """
        with io.open(self.filename, encoding='utf-8') as f:
            self._data = util.deserialize_config(f.read())

    def flush(self, filename=None):
        """Flushes configuration to a file as JSON-ified string.
        If a new filename is not given, uses `filename` property.
        """
        if self._data is None:
            return # no data loaded yet
        if filename is None:
            filename = self.filename
        with open(self.filename, 'w') as f:
            f.write(util.serialize_config(self._data))

    @property
    def author(self):
        """ Getter for configuration file author.
        :returns str: """
        return self._data.get('author', None)

    @property
    def comment(self):
        """ Getter for configuration file comment.
        :returns str: """
        return self._data.get('comment', None)

    # Note: expires and timestamp are required fields, so
    # we don't need to specify defaults in `get` call.
    @property
    def expires(self):
        """ Getter for configuration file expiry date.
        :returns datetime.datetime: """
        return self._data.get('expires')

    @property
    def timestamp(self):
        """ Getter for configuration file timestamp
        :returns datetime.datetime: """
        return self._data.get('timestamp')

    @property
    def policies(self):
        """ Getter for TLS policies in this configuration file.
        :returns list: """
        return self._data.get('policies')

    def policies_iter(self):
        """ Iterates TLS policies in the configuration file.
        Each item is a (mail domain, Policy) tuple.
        """
        for domain in self.policies.keys():
            yield (domain, self.get_policy_for(domain))

    @property
    def pinsets(self):
        """ Getter for pinsets in this configuration file.
        :returns: pinsets """
        return self._data.get('pinsets')

    @property
    def policy_aliases(self):
        """ Getter for policy aliases in this configuration file.
        :returns: policy_aliases """
        return self._data.get('policy-aliases')

    def get_policy_for(self, mail_domain):
        """ Getter for TLS policies in this configuration file.
        If policy is an alias, returns the original policy.
        :param mail_domain str: The e-mail domain (portion after @ sign) to retrieve policy for.
        :returns: Policy dictionary. """
        policy = Policy(self.policies.get(mail_domain))
        if policy.alias is not None:
            return Policy(self.policy_aliases[policy.alias])
        return policy
