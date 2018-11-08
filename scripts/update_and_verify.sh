#!/bin/sh

# Depends on wget and gpgv
# Since this tries to modify an /etc/ directory, should be
# run with escalated permissions.

set -e

JSON_FILE="policy.json"
SIG_FILE="$JSON_FILE.asc"

REMOTE_DIR="https://dl.eff.org/starttls-everywhere"
LOCAL_DIR="/etc/starttls-policy"

TMP_DIR="$(mktemp -d)"
TMP_EXT="tmp"

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

"$(dirname $0)/verify.sh" $LOCAL_DIR $TMP_DIR

# Perform update from tmp => local
mkdir -p $LOCAL_DIR

cp "$TMP_DIR/$JSON_FILE" "$LOCAL_DIR/$JSON_FILE.$TMP_EXT"
cp "$TMP_DIR/$SIG_FILE" "$LOCAL_DIR/$SIG_FILE.$TMP_EXT"

mv "$LOCAL_DIR/$JSON_FILE.$TMP_EXT" "$LOCAL_DIR/$JSON_FILE"
mv "$LOCAL_DIR/$SIG_FILE.$TMP_EXT" "$LOCAL_DIR/$SIG_FILE"

exit 0
