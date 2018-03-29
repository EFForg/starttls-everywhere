""" Utils for transforming and linting the config. """

import datetime
import io
import json
import six
from dateutil import parser # Dependency: python-dateutil


# Duck typing because it's important that the policies are
# well-formed. Until we get a better type system.

class ConfigError(ValueError):
    """ Configuration error. """
    def __init__(self, message):
        # pylint: disable=useless-super-delegation
        super(ConfigError, self).__init__(message)

# The below enforce_* functions each return boolean functions
# that take in a `value` and a `context`.
# These functions enforce some quality about the `value`, in a
# `context` (which is the top-level-object that contains the value).

def enforce_in(possible):
    """ Enforcer that ensures `value` is in `possible`."""
    return lambda val, *unused: val in possible

def enforce_type(type_):
    """ Enforcer that ensures `value` is of type `type_`."""
    return lambda val, *unused: isinstance(val, type_)

def enforce_list(func):
    """ Enforcer that ensures `value` is a list, and that
    `func` returns True for each element in the list."""
    return lambda list_, context=None: \
        isinstance(list_, list) and all(func(val, context) for val in list_)

def enforce_schema(spec):
    """ Enforcer that ensures `value` matches a schema `spec`. """
    return lambda val, context=None: isinstance(val, dict) and \
                                     check_schema(val, spec, False, context)

def enforce_fields(func):
    """ Enforcer that ensures `value` is a dict, and that `func` returns `True`
    for all the `values()` in `value` """
    return lambda obj, context=None: all(func(value, context) for value in obj.values())

def enforce_disallow(*unused):
    """ Enforcer that never returns True. This effectively disallows a field! """
    # pylint: disable=unused-argument
    return False

def enforce_in_context_field(field_name):
    """ Enforcer that ensures `value` is in context[field_name]"""
    return lambda val, parent: val in parent[field_name]

def _get_properties(schema):
    if isinstance(schema, dict):
        enforce = schema['enforce'] if 'enforce' in schema else None
        default = schema['default'] if 'default' in schema else None
        required = schema['required'] if 'required' in schema else False
        return enforce, default, required
    return schema, None, None

def check_schema(obj, schema, error=True, context=None):
    """ Checks to see that each field of `obj`, if defined by `schema`,
    conforms to the specifications set by `schema`."""
    top_level_obj = context
    if top_level_obj is None:
        top_level_obj = obj
    for field, subschema in six.iteritems(schema):
        enforce, default, required = _get_properties(subschema)
        if field not in obj.keys():
            if required and default is None:
                if not error:
                    return False
                raise ConfigError("Field {0} is required!".format(field))
            if default is not None:
                obj[field] = default
            continue
        if enforce is not None and not enforce(obj[field], top_level_obj):
            if not error:
                return False
            raise ConfigError("Field '{0}: {1}' is invalid.".format(field, obj[field]))
    return True

# Extra JSON decoding/encoding helpers

# Encoder
class _ConfigEncoder(json.JSONEncoder):
    """ Defines serializations for objects in the configuration
    that are not natively supported by JSONEncoder.
    Currently, this just includes `datetime` objects.
    """
    def default(self, o):
        # pylint: disable=method-hidden
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%S%z')
        return json.JSONEncoder.default(self, o)

# Decoder
def _policy_config_hook(obj):
    """ Hook to further transform the deserialized configuration object.
    Currently, this just includes transforming time fields from
    epoch seconds or formatted date strings into `datetime` objects.

    :param obj: the object constructed from the JSON string.
    :returns: The fully deserialized object.
    """
    if 'expires' in obj:
        obj['expires'] = _parse_valid_date(obj['expires'])
    if 'timestamp' in obj:
        obj['timestamp'] = _parse_valid_date(obj['timestamp'])
    return obj

def _parse_valid_date(date):
    """ Date parser. `date` can be either an integer (in which it's
    interpreted as seconds since the epoch) or a formatted
    string that `dateutils.parser` can understand."""
    if isinstance(date, int):
        try:
            return datetime.datetime.fromtimestamp(date)
        except (TypeError, ValueError):
            raise ConfigError("Invalid date: {}".format(date))
    try: # Fallback: try to parse a string-like
        return parser.parse(date)
    except (TypeError, ValueError):
        raise ConfigError("Invalid date: {}".format(date))

def deserialize_config(json_string):
    """ Deserializes JSON string into policy config dictionary. """
    config = json.loads(json_string, object_hook=_policy_config_hook)
    try:
        check_schema(config, CONFIG_SCHEMA)
    except ConfigError as e:
        raise ConfigError("Not a well-formed JSON configuration: {}".format(e))
    return config

def serialize_config(config):
    """ Serializes configuartion dictionary into JSON string. """
    return json.dumps(config, cls=_ConfigEncoder)


def config_from_file(filename):
    """ Deserializes JSON string read from `filename` into
    a policy configuration dictionary. """
    with io.open(filename, encoding='utf-8') as f:
        return deserialize_config(f.read())

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
ENFORCE_MODES = ('none', 'testing', 'enforce')

POLICY_SCHEMA = {
        'min-tls-version': {
            'enforce': enforce_in(TLS_VERSIONS),
            'default': 'TLSv1.2',
            },
        'mode': {
            'enforce': enforce_in(ENFORCE_MODES),
            'default': 'testing',
            },
        'mxs': enforce_list(enforce_type(six.string_types)),
        'tls-report': enforce_type(six.string_types),
        'require-valid-certificate': enforce_type(bool),
        'pin': enforce_in_context_field("pinsets"),
        'policy-alias': enforce_in_context_field("policy-aliases"),
        'mta-sts': enforce_type(bool),
        }

POLICY_SCHEMA_NO_ALIAS = dict(POLICY_SCHEMA)
POLICY_SCHEMA_NO_ALIAS.update({
        'policy-alias': enforce_disallow
    })

PINSET_SCHEMA = {
    'static-spki-hashes': enforce_list(enforce_type(six.string_types))
}

CONFIG_SCHEMA = {
        'author': enforce_type(six.string_types),
        'comment': enforce_type(six.string_types),
        'expires': {
            'enforce': enforce_type(datetime.datetime),
            'required': True,
            },
        'timestamp': {
            'enforce': enforce_type(datetime.datetime),
            'required': True,
            },
        'policies': enforce_fields(enforce_schema(POLICY_SCHEMA)),
        'policy-aliases': enforce_fields(enforce_schema(POLICY_SCHEMA_NO_ALIAS)),
        'pinsets': enforce_fields(enforce_schema(PINSET_SCHEMA))
        }
