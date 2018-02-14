#!/bin/bash

./scripts/setup_dns.sh
./scripts/setup.sh
./tests/libs/bats/bin/bats tests/integration_recipient.bats

