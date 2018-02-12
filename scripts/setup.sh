
cp "/opt/starttls-everywhere/postfix-config-$NAME.cf" /etc/postfix/main.cf
ln -sf "/opt/starttls-everywhere/certificates" /etc/certificates

if [[ -e /var/spool/postfix/pid/master.pid ]]
then
    rm /var/spool/postfix/pid/master.pid
fi
cp ./certbot-postfix/certbot_postfix/test_data/config.json .

certbot install --installer certbot-postfix:postfix --cert-path /etc/certificates/valid.crt --key-path /etc/certificates/valid.key -d valid.example-recipient.com
# service postfix stop

# service dnsmasq restart
# service postfix restart
# service postfix reload
