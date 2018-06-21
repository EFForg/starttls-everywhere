#!/bin/sh

# Depends on wget and gpg 2.*.
# Since this tries to modify an /etc/ directory, should be
# run with escalated permissions.

set -e

JSON_FILE="policy.json"
SIG_FILE="$JSON_FILE.asc"

REMOTE_DIR="https://dl.eff.org/starttls-everywhere"
LOCAL_DIR="/etc/starttls-policy"

KEY_ID="B693F33372E965D76D55368616EEA65D03326C9D"
SIGNING_KEY="842AEA40C5BCD6E1"

TMP_DIR="$(mktemp -d)"
TMP_EXT="tmp"

clean_and_exit() {
    rc=$?
    rm -rf "$TMP_DIR"
    exit $rc
}

# traps on regular exit, SIGHUP SIGINT SIGQUIT SIGTERM
trap clean_and_exit 0 1 2 3 15

wget --quiet "$REMOTE_DIR/$JSON_FILE" -O "$TMP_DIR/$JSON_FILE"
wget --quiet "$REMOTE_DIR/$SIG_FILE" -O "$TMP_DIR/$SIG_FILE"

gpg --list-keys "$KEY_ID" >/dev/null 2>&1 || gpg --recv-key "$KEY_ID"
gpg --trusted-key "$SIGNING_KEY" --verify "$TMP_DIR/$SIG_FILE"

mkdir -p $LOCAL_DIR

cp "$TMP_DIR/$JSON_FILE" "$LOCAL_DIR/$JSON_FILE.$TMP_EXT"
cp "$TMP_DIR/$SIG_FILE" "$LOCAL_DIR/$SIG_FILE.$TMP_EXT"

mv "$LOCAL_DIR/$JSON_FILE.$TMP_EXT" "$LOCAL_DIR/$JSON_FILE"
mv "$LOCAL_DIR/$SIG_FILE.$TMP_EXT" "$LOCAL_DIR/$SIG_FILE"

exit 0
