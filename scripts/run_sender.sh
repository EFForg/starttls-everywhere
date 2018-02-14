#!/bin/bash
./scripts/setup_dns.sh
./scripts/setup.sh

mutt -s "This is a subject." root@valid.example-recipient.com < test-email.txt
