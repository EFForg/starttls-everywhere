#!/bin/bash
./setup_dns.sh
./setup.sh
./tests/libs/bats/bin/bats tests/integration_recipient.bats

