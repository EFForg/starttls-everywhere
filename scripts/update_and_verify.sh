#!/bin/sh

# Depends on wget and gpgv
# Since this tries to modify an /etc/ directory, should be
# run with escalated permissions.

set -e

JSON_FILE="policy.json"
SIG_FILE="$JSON_FILE.asc"

REMOTE_DIR="https://dl.eff.org/starttls-everywhere"
LOCAL_DIR="/etc/starttls-policy"

AUTHORITY_FINGERPRINT="B693F33372E965D76D55368616EEA65D03326C9D"

TMP_DIR="$(mktemp -d)"
TMP_EXT="tmp"

clean_and_exit() {
    rc=$?
    rm -rf "$TMP_DIR"
    exit $rc
}

# traps on regular exit, SIGHUP SIGINT SIGQUIT SIGTERM
trap clean_and_exit 0 1 2 3 15

# This is OpenPGP certificate B693F33372E965D76D55368616EEA65D03326C9D
# in RFC4880#section-11.1 Transferable Public Key format:
base64 -d >"$TMP_DIR/authority.key" <<EOF
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
S/SBhVRBN8L4SJ3ywKB86jnDalI=
EOF

wget --quiet "$REMOTE_DIR/$JSON_FILE" -O "$TMP_DIR/$JSON_FILE"
wget --quiet "$REMOTE_DIR/$SIG_FILE" -O "$TMP_DIR/$SIG_FILE"

gpgv --status-fd 3 3>"$TMP_DIR/gpgv.status" --keyring="$TMP_DIR/authority.key" "$TMP_DIR/$SIG_FILE" "$TMP_DIR/$JSON_FILE"

get_sig_epoch_date() {
    awk '($1 == "[GNUPG:]" && $2 == "VALIDSIG" && $12 == "'$AUTHORITY_FINGERPRINT'") { print $5 }'
}

if [ -r "$LOCAL_DIR/$JSON_FILE" ] && [ -r "$LOCAL_DIR/$SIG_FILE" ] ; then
    gpgv --status-fd 3 3>"$TMP_DIR/gpgv.old.status" --keyring="$TMP_DIR/authority.key" "$LOCAL_DIR/$SIG_FILE" "$LOCAL_DIR/$JSON_FILE"
    OLD_DATE=$(get_sig_epoch_date < "$TMP_DIR/gpgv.old.status")
    NEW_DATE=$(get_sig_epoch_date < "$TMP_DIR/gpgv.status")
    if [ $NEW_DATE -lt $OLD_DATE ] ; then
        printf "Rollback detected (old date %d, new date %d)!\n" "$OLD_DATE" "$NEW_DATE" >&2
        exit 1
    fi
fi

mkdir -p $LOCAL_DIR

cp "$TMP_DIR/$JSON_FILE" "$LOCAL_DIR/$JSON_FILE.$TMP_EXT"
cp "$TMP_DIR/$SIG_FILE" "$LOCAL_DIR/$SIG_FILE.$TMP_EXT"

mv "$LOCAL_DIR/$JSON_FILE.$TMP_EXT" "$LOCAL_DIR/$JSON_FILE"
mv "$LOCAL_DIR/$SIG_FILE.$TMP_EXT" "$LOCAL_DIR/$SIG_FILE"

exit 0
