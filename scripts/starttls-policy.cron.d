SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

0 */12 * * * root perl -e "sleep int(rand(3600))" && /bin/sh ./update_and_verify.sh
