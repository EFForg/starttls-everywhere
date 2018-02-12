## Postfix plugin for Certbot
TODO: clean this up (sydli)

This Certbot plugin configures Postfix securely. In particular, what we do is:

1. Fetches a certificate for this email domain, via any of the existing
   certbot plugins.
2. Configures MTA server to:
    - Request STARTTLS by default 
    - Use certs for TLS negotiation.
3. Configures MTA client to:
    - Advertise STARTTLS by default
    - Validate certs
    - Use EFF's STARTTLS policy list.
4. [TODO] Advertise MTA-STS policy.
5. [TODO] Offer TLSRPT enhancement?


## Installation
To install this plugin, ... TODO


TODO:
 - [] Finish configuring per-domain policies
 - [X] Refactor postfix configuration parser
 - [] Finish containerizing and integration tests so the policy stuff works for sure.
 - [] Fix configuration parser to edit master.cf


Centos 6:
 - postfix 2.6.6-8

Debian wheezy (7):
 - postfix 2.9.6-2

Debian jessie (8):
 - postfix 2.11.3-1+deb8u2

Debian stable (current)
 - postfix 3.1.6-0+deb9u1

Ubuntu trusty (14.04):
 - postfix 2.11.0-1

```
	# Postfix has changed support for TLS features, supported protocol versions
	# KEX methods, ciphers et cetera over the years. We sort out version dependend
	# differences here and pass them onto other configuration functions.
	# see:
	#  http://www.postfix.org/TLS_README.html
	#  http://www.postfix.org/FORWARD_SECRECY_README.html

	# Postfix == 2.2:
	# - TLS support introduced via 3rd party patch, see:
	#   http://www.postfix.org/TLS_LEGACY_README.html
	
	# Postfix => 2.2:
	# - built-in TLS support added
	# - Support for PFS introduced
	# - Support for (E)DHE params >= 1024bit (need to be generated), default 1k

	# Postfix => 2.5:
	# - Syntax to specify mandatory protocol version changes:
	#   *  < 2.5: `smtpd_tls_mandatory_protocols = TLSv1`
	#   * => 2.5: `smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3`
	# - Certificate fingerprint verification added

	# Postfix => 2.6:
	# - Support for ECDHE NIST P-256 curve (enable `smtpd_tls_eecdh_grade = strong`)
	# - Support for configurable cipher-suites and protocol versions added, pre-2.6 
	#   releases always set EXPORT, options: `smtp_tls_ciphers` and `smtp_tls_protocols`
	# - `smtp_tls_eccert_file` and `smtp_tls_eckey_file` config. options added
	
	# Postfix => 2.8:
	# - Override Client suite preference w. `tls_preempt_cipherlist = yes`
	# - Elliptic curve crypto. support enabled by default
	
	# Postfix => 2.9:
	# - Public key fingerprint support added
	# - `permit_tls_clientcerts`, `permit_tls_all_clientcerts` and
	#   `check_ccert_access` config. options added

	# Postfix <= 2.9.5:
	# - BUG: Public key fingerprint is computed incorrectly

	# Postfix => 3.1:
	# - Built-in support for TLS management and DANE added, see:
	#   http://www.postfix.org/postfix-tls.1.html

```
