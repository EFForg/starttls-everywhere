#!./tests/libs/bats/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'

@test "server advertises STARTTLS" {
    nc -v localhost 25 <<< "EHLO valid.example-recipient.com" | grep "STARTTLS"
    assert_success
}

@test "client advertises STARTTLS" {
    nc -v localhost 25 <<< "STARTTLS" | grep "Ready to start TLS"
    assert_success
}

@test "performs TLS handshake correctly" {
    openssl s_client -connect valid.example-recipient.com:25 -starttls smtp -tls1 | grep "Verify return code: 0 (ok)"
    assert_success
}

@test "sends mail correctly" {
    mutt -s "This is a subject." root@valid.example-recipient.com < test-email.txt
    sleep 1
    assert [ -s '/var/mail/root' ]
    cat /var/mail/root | grep "This is a subject."
    assert_success
}
