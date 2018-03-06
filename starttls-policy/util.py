from functools import partial
import datetime
import json
from dateutil import parser # Dependency: python-dateutil

# Duck typing because it's important that the policies are
# well-formed. Until we get a better type system.

class ConfigError(ValueError):
    def __init__(self, message):
        super(self.__class__, self).__init__(message)

def _enforce_in(possible):
    return lambda val: val in possible

def _parse_valid_date(date):
    if isinstance(date, int):
        try:
            return datetime.datetime.fromtimestamp(date)
        except (TypeError, ValueError):
            raise ConfigError("Invalid date: {}".format(date))
    try: # Fallback: try to parse a string-like
        return parser.parse(date)
    except (TypeError, ValueError):
        raise ConfigError("Invalid date: {}".format(date))

def _enforce_valid_date(date):
    return isinstance(date, datetime.datetime)

def _enforce_type(type):
    return lambda val: isinstance(val, type)

def _enforce_list(func):
    return lambda l: isinstance(l, list) and all(func(val) for val in l)

def _enforce_object(spec):
    return lambda val: isinstance(val, dict) and _check_schema(val, spec) is not None

def _enforce_fields(func):
    return lambda obj: all(func(value) for value in obj.values())

def _get_properties(schema):
    if isinstance(schema, dict):
        enforce = schema['enforce'] if 'enforce' in schema else None
        default = schema['default'] if 'default' in schema else None
        required = schema['required'] if 'required' in schema else False
        return enforce, default, required
    else:
        return schema, None, None

def _check_schema(obj, schema):
    for field, subschema in schema.iteritems():
        enforce, default, required = _get_properties(subschema)
        if field not in obj.keys():
            if required and default is None:
                raise ConfigError("Field {0} is required!".format(field))
            obj[field] = default
            continue
        if enforce is not None and not enforce(obj[field]):
            raise ConfigError("Field '{0}: {1}' is invalid.".format(field, obj[field]))
    return True

# JSON schema definitions.
# All in one place!

# Each schema definition (for a particular field) has three possible
# entries: `enforce`, `default`, and `required`.
# `enforce`  function that expects to return True when called on
#            the field; otherwise, `ConfigError` is raised.
# `default`  default value of this field, if it is not specified.
# `required` if True, then ConfigError is thrown if this field is not specified
#            and there is no default value.

DEFAULT_FILENAME = "config.json"

TLS_VERSIONS = ('TLSv1', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3')
ENFORCE_MODES = ('none', 'testing', 'enforce')

POLICY_SCHEMA = {
        'min-tls-version': {
            'enforce': _enforce_in(TLS_VERSIONS),
            'default': 'TLSv1.2',
            },
        'mode': {
            'enforce': _enforce_in(ENFORCE_MODES),
            'default': 'testing',
            },
        'mxs': _enforce_list(_enforce_type(unicode)),
        'tls-report': _enforce_type(unicode),
        'require-valid-certificate': _enforce_type(bool),
        }

CONFIG_SCHEMA = {
        'author': _enforce_type(unicode),
        'comment': _enforce_type(unicode),
        'expires': {
            'enforce': _enforce_valid_date,
            'required': True,
            },
        'timestamp': {
            'enforce': _enforce_valid_date,
            'required': True,
            },
        'tls-policies': _enforce_fields(_enforce_object(POLICY_SCHEMA)),
        }

# Extra JSON decoding/encoding helpers

# Encoder
class ConfigEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S%z')
        return json.JSONEncoder.default(self, obj)

# Decoder
def _config_hook(obj):
    if 'expires' in obj:
        obj['expires'] = _parse_valid_date(obj['expires'])
    if 'timestamp' in obj:
        obj['timestamp'] = _parse_valid_date(obj['timestamp'])
    return obj

# Exports
def deserialize_config(json_string):
    config = json.loads(json_string, object_hook=_config_hook)
    try: 
        _check_schema(config, CONFIG_SCHEMA)
    except ConfigError as e:
        raise ConfigError("Not a well-formed JSON configuration: {}".format(e))
    return config

def serialize_config(config):
    return json.dumps(config, cls=ConfigEncoder)

