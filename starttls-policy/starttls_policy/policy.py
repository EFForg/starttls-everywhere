""" Policy config wrapper """
import collections
import logging
import datetime
import io
import json
import six
from starttls_policy import util
from starttls_policy import constants

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


# Encoder
class ConfigEncoder(json.JSONEncoder):
    """ Defines serializations for objects in the configuration
    that are not natively supported by JSONEncoder.
    Currently, this just includes `datetime` objects.
    """
    def default(self, o):
        # pylint: disable=method-hidden
        if isinstance(o, MergableConfig):
            return o.get_dict()
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%S%z')
        return json.JSONEncoder.default(self, o)

class MergableConfig(object):
    # pylint: disable=useless-object-inheritance
    """Top level config object class for merging properties.
    """

    def __init__(self, schema):
        self._schema = schema
        self._data = {}

    def _set_attr(self, attr, value):
        enforcer, _, _ = util.get_properties(self._schema[attr])
        if not callable(enforcer):
            raise util.ConfigError('Attribute {} has no enforcer'.format(attr))
        try:
            self._data[attr] = enforcer(value)
        except util.ConfigError as e:
            raise util.ConfigError('Error for attribute {}: '.format(attr) + str(e))

    def _check_against_schema(self):
        for key, subschema in six.iteritems(self._schema):
            _, default, required = util.get_properties(subschema)
            if key not in self._data and default:
                setattr(self, util.as_attr(key), default)
            if key not in self._data and required:
                raise util.ConfigError('Attribute {} is required.'.format(key))

    def get_dict(self):
        """ Returns internal dictionary representation of data. """
        return self._data

    def load_from_dict(self, dict_):
        """ Sets Config attributes from key/values in dict_ """
        for key, value in six.iteritems(dict_):
            setattr(self, util.as_attr(key), value)
        self._check_against_schema()

    def dump(self):
        """ Serializes to a string """
        return json.dumps(self._data, cls=ConfigEncoder)

    def should_update(self, newer_config):
        """Overwritable. If this function returns true, then any call to `update`
        will succeed.
        """
        # pylint: disable=unused-argument
        return True

    def update(self, newer_config, merge=False):
        """Create a fresh config combining the new and old configs.

        It does this by iterating over the 'config_properties' class
        attribute which contains names of property attributes for the config.

        Two methods of combining configs are possible, an 'update' and
        a 'merge', the latter set by the keyword argument 'merge=True'.

        An update overrides older values with new values -- even if those
        new values are None.  Update will remove values that are present in
        the old config if they are not present in the new config.

        A merge by comparison will allow old values to persist if they are
        not specified in the new config.  This can be used for end-user
        customizations to override specific settings without having to re-create
        large portions of a config to override it.

        Arguments:
          newer_config: A config object to combine with the current config.
          merge: Allows old values not overridden to survive into the fresh config.

        Returns:
          A config object of the same sort as called upon.
        """
        # removed 'merge' kw arg - and it was passed to constructor
        # make a note to not do that, consume it on the param list
        fresh_config = self.__class__(schema=self._schema)
        logger.debug('from parent update merge %s', merge)
        if not isinstance(newer_config, self.__class__):
            raise util.ConfigError('Attempting to update a %s with a %s' % (
                self.__class__,
                newer_config.__class__))
        for prop_name in self._schema.keys():
            # get the specified property off of the current class
            prop = self.__class__.__dict__.get(util.as_attr(prop_name))
            assert prop
            new_value = prop.fget(newer_config)
            old_value = prop.fget(self)
            if merge and new_value is not None:
                if isinstance(new_value, dict) and isinstance(old_value, dict):
                    new_value = old_value.update(new_value)
                elif isinstance(new_value, list) and isinstance(old_value, list):
                    new_value = old_value.extend(new_value)
            if new_value is not None:
                prop.fset(fresh_config, new_value)
            elif merge and old_value is not None:
                prop.fset(fresh_config, old_value)
        return fresh_config

    def merge(self, newer_config, **kwargs):
        """Combines configs and keeps old values if they are not overridden.

        See docstring for 'update' method for more details.

        Arguments:
          newer_config: A config object to combine with the current config.
          merge: Allows old values not overridden to survive into the fresh config.

        Returns:
          A config object of the same sort as called upon.
        """
        kwargs['merge'] = True
        logger.debug('from parent merge: %s', kwargs)
        return self.update(newer_config, **kwargs)

class Policy(MergableConfig):
    """Class containing a single TLS policy information for a particular e-mail domain.
    """
    def __init__(self, data=None, pinsets=None, aliases=None, schema=util.POLICY_SCHEMA):
    # pylint: disable=dangerous-default-value
        super(Policy, self).__init__(schema)
        self.pinsets = pinsets
        self.aliases = aliases
        self._data = {}
        if data is not None:
            self.load_from_dict(data)

    @property
    def mode(self):
        """ Getter for this policy's minimum TLS version.
        :returns str: """
        return self._data.get('mode', None)

    @mode.setter
    def mode(self, value):
        """ Setter for this policy's minimum TLS version.
        :returns str: """
        self._set_attr('mode', value)

    @property
    def min_tls_version(self):
        """ Getter for this policy's minimum TLS version.
        :returns str: """
        return self._data.get('min-tls-version', None)

    @min_tls_version.setter
    def min_tls_version(self, value):
        """ Setter for this policy's minimum TLS version.
        :returns str: """
        self._set_attr('min-tls-version', value)

    @property
    def mxs(self):
        """ Getter for the mx hosts that this domain's certs can be valid for.
        :returns list: """
        return self._data.get('mxs', [])

    @mxs.setter
    def mxs(self, value):
        """ Setter for the mx hosts that this domain's certs can be valid for.
        :returns list: """
        self._set_attr('mxs', value)

    # TODO: enforce https: or mailto: protocol on this string
    @property
    def tls_report(self):
        """ Getter for the tls reporting endpoint for this policy
        :returns list: """
        return self._data.get('tls-report', None)

    @tls_report.setter
    def tls_report(self, value):
        """ Setter for the tls reporting endpoint for this policy
        :returns list: """
        self._set_attr('tls-report', value)

    @property
    def pin(self):
        """ Getter for the pinned keys for this policy
        :returns list: """
        return self._data.get('pin', None)

    @pin.setter
    def pin(self, value):
        """ Setter for the pinned keys for this policy
        :returns list: """
        if value not in self.pinsets:
            raise util.ConfigError(
                "Pin {} not specified in config, or it wasn't set before policies.".format(value))
        self._set_attr('pin', value)

    @property
    def mta_sts(self):
        """ Getter for whether this policy supports MTA STS.
        :returns bool: """
        return self._data.get('mta-sts', False)

    @mta_sts.setter
    def mta_sts(self, value):
        """ Setter for whether this policy supports MTA STS.
        :returns bool: """
        self._set_attr('mta-sts', value)

    @property
    def policy_alias(self):
        """ Getter for this policy's alias, if it exists.
        :returns str: """
        return self._data.get('policy-alias', None)

    @policy_alias.setter
    def policy_alias(self, value):
        """ Setter for this policy's alias, if it exists.
        :returns str: """
        if value not in self.aliases:
            raise util.ConfigError(
                "Alias {} not specified in config, or it wasn't set before policies.".format(value))
        self._set_attr('policy-alias', value)

class PolicyNoAlias(Policy):
    """ Same as Policy, but forbids setting policy_alias field.
    """
    @property
    def policy_alias(self):
        """ This type of policy can't be aliased. Returns None."""
        pass

    @policy_alias.setter
    def policy_alias(self, value):
        """ This type of policy can't be aliased. Throws an error on access."""
        # pylint: disable=unused-argument
        raise util.ConfigError('PolicyNoAlias object cannot have policy-alias field!')

class Config(MergableConfig, collections.Mapping):
    """Class for retrieving properties in TLS Policy config.
    If `pinsets` and `policy_aliases` are specified, they must be set
    before `policies`, so policy format validation can work properly.
    """

    def __getitem__(self, key):
        return self.get_policy_for(key)

    def __len__(self):
        return len(self.policies)

    def __iter__(self):
        """ Iterates TLS policies in the configuration file.
        Each item is a (mail domain, Policy) tuple.
        """
        for domain in self.keys():
            yield domain

    def keys(self):
        if self.policies is None:
            return set([])
        return self.policies.keys()

    def __init__(self, filename=constants.POLICY_LOCAL_FILE, schema=util.CONFIG_SCHEMA):
    # pylint: disable=dangerous-default-value
        super(Config, self).__init__(schema)
        self.filename = filename

    def load(self):
        """Loads JSON configuration from file specified by `filename` property.
        """
        with io.open(self.filename, encoding='utf-8') as f:
            self.load_from_dict(json.loads(f.read()))

    def load_from_dict(self, dict_):
        """ Sets Config attributes from key/values in dict_
        Also ensures that pinsets and aliases are parsed before
        policies. """
        policies = dict_.get('policies', None)
        super(Config, self).load_from_dict(
            {k: v for k, v in six.iteritems(dict_) if k != 'policies'})
        if policies is not None:
            self.policies = policies

    def flush(self, filename=None):
        """Flushes configuration to a file as JSON-ified string.
        If a new filename is not given, uses `filename` property.
        """
        if filename is None:
            filename = self.filename
        with open(filename, 'w') as f:
            f.write(self.dump())

    @property
    def author(self):
        """ Getter for configuration file author.
        :returns str: """
        return self._data.get('author', None)

    @author.setter
    def author(self, value):
        """ Setter for configuration file author.
        :returns str: """
        self._set_attr('author', value)

    # Note: expires and timestamp are required fields, so
    # we don't need to specify defaults in `get` call.
    @property
    def expires(self):
        """ Getter for configuration file expiry date.
        :returns datetime.datetime: """
        return self._data.get('expires')

    @expires.setter
    def expires(self, value):
        """ Setter for configuration file expiry date.
        :returns datetime.datetime: """
        value = util.parse_valid_date(value)
        self._set_attr('expires', value)

    @property
    def timestamp(self):
        """ Getter for configuration file timestamp
        :returns datetime.datetime: """
        return self._data.get('timestamp')

    @timestamp.setter
    def timestamp(self, value):
        """ Setter for configuration file timestamp
        :returns datetime.datetime: """
        value = util.parse_valid_date(value)
        self._set_attr('timestamp', value)

    @property
    def policies(self):
        """ Getter for TLS policies in this configuration file.
        :returns list: """
        return self._data.get('policies')

    @policies.setter
    def policies(self, value):
        """ Setter for TLS policies in this configuration file.
        If policies contains pins or refers to policy_aliases, note
        that these fields should be set *first* so the policies can
        validate correctly.
        :returns list: """
        policies = {}
        for domain, obj in six.iteritems(value):
            if isinstance(obj, Policy):
                policies[domain] = obj
            else:
                policies[domain] = Policy(obj, self.pinsets, self.policy_aliases)
        self._set_attr('policies', policies)

    @property
    def pinsets(self):
        """ Getter for pinsets in this configuration file.
        :returns: pinsets """
        return self._data.get('pinsets', {})

    @pinsets.setter
    def pinsets(self, value):
        """ Setter for pinsets in this configuration file.
        :returns: pinsets """
        self._set_attr('pinsets', value)

    @property
    def policy_aliases(self):
        """ Getter for policy aliases in this configuration file.
        :returns: policy_aliases """
        return self._data.get('policy-aliases', {})

    @policy_aliases.setter
    def policy_aliases(self, value):
        """ Setter for policy aliases in this configuration file.
        :returns: policy_aliases """
        policies = {}
        for domain, obj in six.iteritems(value):
            policies[domain] = PolicyNoAlias(obj, self.pinsets)
        self._set_attr('policy-aliases', policies)

    def get_policy_for(self, mail_domain):
        """ Getter for TLS policies in this configuration file.
        If policy is an alias, returns the original policy.
        :param mail_domain str: The e-mail domain (portion after @ sign) to retrieve policy for.
        :returns: Policy dictionary. """
        policy = self.policies.get(mail_domain)
        if policy.policy_alias is not None:
            return self.policy_aliases[policy.policy_alias]
        return policy
