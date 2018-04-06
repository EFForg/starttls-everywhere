""" Utils for transforming and linting the config. """

import datetime
from functools import partial
import six
from dateutil import parser # Dependency: python-dateutil


class ConfigError(ValueError):
    """ Configuration error. """
    def __init__(self, message):
        # pylint: disable=useless-super-delegation
        super(ConfigError, self).__init__(message)


# The below enforce_* functions each enforce some quality about a `value`.
# If this quality is not achieved, a `ConfigError` is raised.

def enforce_in(possible, val):
    """ Enforcer that ensures `value` is in `possible`."""
    if val not in possible:
        raise ConfigError('Configuration value {} is not one of {}'.format(
                              val, ', '.join(possible)))
    return val

def enforce_type(type_, val):
    """ Enforcer that ensures `value` is of type `type_`."""
    if not isinstance(val, type_):
        raise ConfigError('Configuration value {} is not of type {}'.format(
                              val, type_))
    return val

def enforce_list(enforcer, list_):
    """ Enforcer that ensures `value` is a list, and that
    `enforcer` returns True for each element in the list."""
    try:
        all(enforcer(val) for val in list_)
    except TypeError as e:
        raise ConfigError('Configuration value {} has a bad type: '.format(list_) + str(e))
    return list_

def enforce_fields(enforcer, obj):
    """ Enforcer that ensures `value` is a dict, and that `func` returns `True`
    for all the `values()` in `value` """
    try:
        all(enforcer(val) for val in obj.values())
    except TypeError as e:
        raise ConfigError('Configuration value {} has a bad type: '.format(obj) + str(e))
    return obj

# Extra JSON decoding/encoding helpers

def as_attr(s):
    """ Replaces dashes with underscores, so `s` can be a python attribute :) """
    return s.replace('-', '_')

def parse_valid_date(date):
    """ Date parser. `date` can be either an integer (in which it's
    interpreted as seconds since the epoch) or a formatted
    string that `dateutils.parser` can understand."""
    if isinstance(date, datetime.datetime):
        return date
    if isinstance(date, int):
        try:
            return datetime.datetime.fromtimestamp(date)
        except (TypeError, ValueError):
            raise ConfigError("Invalid date: {}".format(date))
    try: # Fallback: try to parse a string-like
        return parser.parse(date)
    except (TypeError, ValueError):
        raise ConfigError("Invalid date: {}".format(date))

def get_properties(schema):
    """ Return the three properties we have to enforce for this schema.
    Returns tuple of (enforce, default, and required), where
    enforce is a custom function, default is the default value for this attribute, and
    required is a boolean.
    """
    if isinstance(schema, dict):
        enforce = schema['enforce'] if 'enforce' in schema else None
        default = schema['default'] if 'default' in schema else None
        required = schema['required'] if 'required' in schema else False
        return enforce, default, required
    return schema, None, None

# JSON schema definitions.
# All in one place!
#
# Each schema definition (for a particular field) has three possible
# entries: `enforce`, `default`, and `required`.
# `enforce`  function that expects to return True when called on
#            the field; otherwise, `ConfigError` is raised.
# `default`  default value of this field, if it is not specified.
# `required` if True, then ConfigError is thrown if this field is not specified
#            and there is no default value.

TLS_VERSIONS = ('TLSv1', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3')
ENFORCE_MODES = ('testing', 'enforce')

POLICY_SCHEMA = {
        'min-tls-version': {
            'enforce': partial(enforce_in, TLS_VERSIONS),
            'default': 'TLSv1.2',
            },
        'mode': {
            'enforce': partial(enforce_in, ENFORCE_MODES),
            'default': 'testing',
            },
        # TODO (#50) Validate mxs as FQDNs (using public suffix list)
        'mxs': {
            'enforce': partial(enforce_list, partial(enforce_type, six.string_types)),
            'default': [],
            },
        # TODO (#50) Validate reporting endpoint as https: or mailto:
        'tls-report': partial(enforce_type, six.string_types),
        'pin': partial(enforce_type, six.string_types),
        'policy-alias': partial(enforce_type, six.string_types),
        'mta-sts': partial(enforce_type, bool),
        }

PINSET_SCHEMA = {
    'static-spki-hashes': partial(enforce_list, partial(enforce_type, six.string_types))
}

CONFIG_SCHEMA = {
        'author': partial(enforce_type, six.string_types),
        'expires': {
            'enforce': partial(enforce_type, datetime.datetime),
            'required': True,
            },
        'timestamp': {
            'enforce': partial(enforce_type, datetime.datetime),
            'required': True,
            },
        'policies': partial(enforce_fields, partial(enforce_type, object)),
        'policy-aliases': partial(enforce_fields, partial(enforce_type, object)),
        'pinsets': partial(enforce_fields, partial(enforce_type, object))
        }
