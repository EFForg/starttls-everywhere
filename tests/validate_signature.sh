#!/bin/sh

# Arguments:
# ./validate_signature.sh <path-to-policy.json> <path-to-policy.json.asc>

set -e

JSON_FILE="policy.json"
SIG_FILE="$JSON_FILE.asc"

REMOTE_DIR="https://dl.eff.org/starttls-everywhere"

TMP_DIR="$(mktemp -d)"

clean_and_exit() {
    rc=$?
    rm -rf "$TMP_DIR"
    exit $rc
}

# traps on regular exit, SIGHUP SIGINT SIGQUIT SIGTERM
trap clean_and_exit 0 1 2 3 15

# Fetch remote source
wget --quiet "$REMOTE_DIR/$JSON_FILE" -O "$TMP_DIR/$JSON_FILE"
wget --quiet "$REMOTE_DIR/$SIG_FILE" -O "$TMP_DIR/$SIG_FILE"

./scripts/verify.sh $TMP_DIR ./
