"""
Config generator
"""
import abc
import os
import sys
import six

from starttls_policy import policy
from starttls_policy import update
from starttls_policy import constants

class ConfigGenerator(object):
    """
    Generic configuration generator.
    The two primary public functions:
        generate()
        print_instruct()
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, policy_dir, output=sys.stdout):
        self._policy_dir = policy_dir
        self._policy_filename = os.path.join(self._policy_dir, constants.POLICY_FILENAME)
        self._policy_config = None
        self._output = output

    def _create_config(self):
        if self._policy_config is None:
            update.update(filename=self._policy_filename, force_update=True)
            self._policy_config = policy.Config(filename=self._policy_filename)
            self._policy_config.load()
        return self._policy_config

    def _write_config(self, result):
        six.print_(result, file=self._output)

    def generate(self):
        policy_list = self._create_config()
        result = self._generate(policy_list)
        self._write_config(result)

    def manual_instructions(self, filename):
        help_install_string = self._instruct_string(filename)
        print(help_install_string)

    @abc.abstractmethod
    def _generate(self, policy_list):
        """Creates configuration file. Returns a unicode string (text to write to file)."""

    @abc.abstractmethod
    def _instruct_string(self, filename):
        """Explain how to install the configuration file that was generated."""

def _policy_for_domain(domain, policy, max_domain_len):
    line = ("{0:%d} " % max_domain_len).format(domain)
    if policy.mode == "enforce":
        line += " secure match="
        line += ",".join(policy.mxs)
    elif policy.mode == "testing":
        line += "may "
    return line

class PostfixGenerator(ConfigGenerator):
    """
    Configuration generator for postfix.
    """

    def __init__(self, policy_dir, output):
        super(PostfixGenerator, self).__init__(policy_dir, output)

    def _generate(self, policy_list):
        policies = []
        max_domain_len = len(max(policy_list, key=len))
        for domain, tls_policy in sorted(policy_list.iteritems()):
            policies.append(_policy_for_domain(domain, tls_policy, max_domain_len))
        return "\n".join(policies)

    def _instruct_string(self, filename):
        abs_path = os.path.abspath(filename)
        return ("\nYou'll need to point your Postfix configuration to %s.\n"
            "Check if `postconf smtp_tls_policy_maps` includes %s.\n"
            "If not, run:\n\n"
            "export POSTFIX_CURRENT_MAPS=$(postconf -h smtp_tls_policy_maps)\n"
            "postconf -e 'smtp_tls_policy_maps=$POSTFIX_CURRENT_MAPS hash:%s'\n\n"
            "And you should be good to go!\n" % (filename, filename, abs_path))
