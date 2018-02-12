#!./tests/libs/bats/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'

@test "recieves an email over TLS" {
    sleep 3
    assert [ -s '/var/mail/root' ]
    cat /var/mail/root | grep "This is a subject."
    assert_success
}

