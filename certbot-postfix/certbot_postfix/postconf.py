"""Classes that wrap the postconf command line utility.

These classes allow you to interact with a Postfix config like it is a
dictionary, with the getting and setting of values in the config being
handled automatically by the class.

"""
import collections

from certbot import errors
from certbot_postfix import util


class ConfigMain(util.PostfixUtilBase):
    """A parser for Postfix's main.cf file."""

    _modifiers = None
    _db = None
    _updated = {}
    """An iterable containing additional CLI flags for postconf."""

    def __init__(self, executable, config_dir=None):
        util.PostfixUtilBase.__init__(self, executable, config_dir)
        self._db = {}
        self._read_from_conf()

    def _read_from_conf(self):
        out = self._get_output()
        for name, value in _parse_main_output(out):
            if not value:
                value = ""
            self._db[name] = value

    def get(self, name):
        if name in self._updated:
            return self._updated[name]
        return self._db[name]

    def set(self, name, value):
        if name not in self._db:
            return # TODO: error here
        # We've updated this name before.
        if name in self._updated:
            if value == self._updated[name]:
                return
            if value == self._db[name]:
                del self._updated[name]
                return
        # We haven't updated this name before.
        else:
            # If we're just setting the default value, ignore.
            if value != self._db[name]:
                self._updated[name] = value
            
    def flush(self):
        if len(self._updated) == 0:
            return
        args = ['-e']
        for name, value in self._updated.iteritems():
            args.append('{0}={1}'.format(name, value))
        try:
            return self._get_output(args)
        except:
            raise errors.PluginError("Unable to save to Postfix config!")

    def _call(self, extra_args=None):
        """Runs Postconf and returns the result.

        If self._modifiers is set, it is provided on the command line to
        postconf before any values in extra_args.

        :param list extra_args: additional arguments for the command

        :returns: data written to stdout and stderr
        :rtype: `tuple` of `str`

        :raises subprocess.CalledProcessError: if the command fails

        """
        all_extra_args = []
        for args_list in (self._modifiers, extra_args,):
            if args_list is not None:
                all_extra_args.extend(args_list)

        return super(ConfigMain, self)._call(all_extra_args)



def _parse_main_output(output):
    """Parses the raw output from Postconf about main.cf.

    :param str output: data postconf wrote to stdout about main.cf

    :returns: generator providing key-value pairs from main.cf
    :rtype: generator

    """
    for line in output.splitlines():
        name, _, value = line.partition(" =")
        yield name, value.strip()


