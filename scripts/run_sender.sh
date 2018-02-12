#!/bin/bash
./setup_dns.sh
./setup.sh

mutt -s "This is a subject." root@valid.example-recipient.com < test-email.txt
