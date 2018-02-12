# Have DNSmasq point mx records at self, and enable root user
echo "selfmx
      user=root" > /etc/dnsmasq.conf

# Do not try this at home!
# Force image to use DNSmasq resolver
echo "nameserver 127.0.0.1" > /etc/resolv.conf

service dnsmasq restart
