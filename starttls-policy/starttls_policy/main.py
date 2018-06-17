import argparse
import os
import sys

from starttls_policy import configure

GENERATORS = {
    "postfix": configure.PostfixGenerator,
}

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-only", help="Update the policy file. " +
                        "If set, no other parameters other than --policy-dir are used.",
                        action="store_true", dest="update_only", required=False)
    parser.add_argument("--generate", help="The MTA you want to generate a configuration file for.",
                        dest="generate", required="--update-only" not in sys.argv)
    # TODO: decide whether to use /etc/ for policy list home
    parser.add_argument("--policy-dir", help="Policy file directory on this computer.",
                        default="/etc/starttls-policy/", dest="policy_dir")
    parser.add_argument("--output", help="Filepath of the configuration file to write output to. " +
                        "If not set, uses stdout.",
                        required=False)
    return parser


def main(cli_args=sys.argv[1:]):
    """ Entrypoint for CLI tool. """
    parser = argument_parser()
    arguments = parser.parse_args()
    if arguments.update_only:
        raise NotImplementedError
    if arguments.generate not in GENERATORS:
        parser.error("no configuration generator exists for '%s'" % arguments.generate)
    output = sys.stdout
    if arguments.output is not None:
        output = open(arguments.output, "w")
    config_generator = GENERATORS[arguments.generate](arguments.policy_dir, output=output)
    config_generator.generate()
    # If we created a file somewhere, make sure permissions on file are not elevated.
    if arguments.output is not None:
        # TODO: does the below work on all distros?
        uid = os.environ.get("SUDO_UID")
        gid = os.environ.get("SUDO_GID")
        if uid is not None:
            os.chown(arguments.output, int(uid), int(gid))
        output.close()
        config_generator.manual_instructions(arguments.output)

if __name__ == "__main__":
    err_string = main()
    if err_string:
        logger.warning("Exiting with message %s", err_string)
    sys.exit(err_string)  # pragma: no cover
