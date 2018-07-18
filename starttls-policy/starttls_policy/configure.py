"""
Config generator
"""
import abc
import os
import sys
import six

from starttls_policy import constants
from starttls_policy import policy

class ConfigGenerator(object):
    """
    Generic configuration generator.
    The two primary public functions:
        generate()
        print_instruct()
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, policy_dir):
        self._policy_dir = policy_dir
        self._policy_filename = os.path.join(self._policy_dir, constants.POLICY_FILENAME)
        self._config_filename = os.path.join(self._policy_dir, self.default_filename)
        self._policy_config = None

    def _load_config(self):
        if self._policy_config is None:
            self._policy_config = policy.Config(filename=self._policy_filename)
            self._policy_config.load()
        return self._policy_config

    def _write_config(self, result, output):
        six.print_(result, file=output)

    def generate(self):
        policy_list = self._load_config()
        result = self._generate(policy_list)
        with open(self._config_filename, "w") as config_file:
            self._write_config(result, config_file)

    def manual_instructions(self):
        six.print_("{line}Manual installation instructions for {mta_name}{line}{instructions}".format(
            line="\n" + ("-" * 50) + "\n", mta_name=self.mta_name, instructions=self._instruct_string()))

    @abc.abstractmethod
    def _generate(self, policy_list):
        """Creates configuration file. Returns a unicode string (text to write to file)."""

    @abc.abstractmethod
    def _instruct_string(self):
        """Explain how to install the configuration file that was generated."""

    @abc.abstractproperty
    def mta_name(self):
        """The name of the MTA this generator is for."""

    @abc.abstractproperty
    def default_filename(self):
        """The expected default filename of the generated configuration file."""

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

    def _generate(self, policy_list):
        policies = []
        max_domain_len = len(max(policy_list, key=len))
        for domain, tls_policy in sorted(six.iteritems(policy_list)):
            policies.append(_policy_for_domain(domain, tls_policy, max_domain_len))
        return "\n".join(policies)

    def _instruct_string(self):
        filename = self._config_filename
        abs_path = os.path.abspath(filename)
        return ("\nFirst, run:\n\n"
            "postmap {abs_path}\n\n"
            "Then, you'll need to point your Postfix configuration to {filename}.\n"
            "Check if `postconf smtp_tls_policy_maps` includes this file.\n"
            "If not, run:\n\n"
            "postconf -e \"smtp_tls_policy_maps=$(postconf -h smtp_tls_policy_maps) hash:{abs_path}\"\n\n"
            "And finally:\n\n"
            "postfix reload\n").format(abs_path=abs_path, filename=filename)

    @property
    def mta_name(self):
        return "Postfix"

    @property
    def default_filename(self):
        return "postfix_tls_policy"
