#!./tests/libs/bats/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'

@test "sends an e-mail" {
    nc -v localhost 25 <<< "EHLO valid.example-recipient.com" | grep "STARTTLS"
    assert_success
}


