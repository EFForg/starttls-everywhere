import argparse
import os
import sys

from starttls_policy import configure
from starttls_policy import constants
from starttls_policy import update

GENERATORS = {
    "postfix": configure.PostfixGenerator,
}

def _argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-only", help="Update the policy file. " +
                        "If set, no other parameters other than --policy-dir are used.",
                        action="store_true", dest="update_only", required=False)
    parser.add_argument("--generate", help="The MTA you want to generate a configuration file for.",
                        dest="generate", required="--update-only" not in sys.argv)
    # TODO: decide whether to use /etc/ for policy list home
    parser.add_argument("--policy-dir", help="Policy file directory on this computer.",
                        default="/etc/starttls-policy/", dest="policy_dir")
    return parser


def _ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def main(cli_args=sys.argv[1:]):
    """ Entrypoint for CLI tool. """
    parser = _argument_parser()
    arguments = parser.parse_args()
    if arguments.update_only:
        _ensure_directory(arguments.policy_dir)
        update.update(filename=os.path.join(arguments.policy_dir, constants.POLICY_FILENAME),
                      force_update=True)
        return
    if arguments.generate not in GENERATORS:
        parser.error("no configuration generator exists for '%s'" % arguments.generate)
    _ensure_directory(arguments.policy_dir)
    config_generator = GENERATORS[arguments.generate](arguments.policy_dir)
    config_generator.generate()
    config_generator.manual_instructions()

if __name__ == "__main__":
    err_string = main()
    if err_string:
        logger.warning("Exiting with message %s", err_string)
    sys.exit(err_string)  # pragma: no cover
