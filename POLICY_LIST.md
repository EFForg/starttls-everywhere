The STARTTLS Policy List is a list of email domains who meet a minimum set of security requirements. By providing a list of email domains that support TLS encryption and present valid certificates, the STARTTLS Policy List gives mailservers another point of reference to discover whether other mailservers support STARTTLS.

You can verify the [list](https://dl.eff.org/starttls-everywhere/policy.json) with the corresponding [PGP signature](https://dl.eff.org/starttls-everywhere/policy.json.asc). You can also read more about a [detailed specification](https://github.com/EFForg/starttls-everywhere/blob/master/RULES.md) of the list's format.

## Using the list

To download and verify the most up-to-date version of the STARTTLS policy list:

```
wget https://dl.eff.org/starttls-everywhere/policy.json
wget https://dl.eff.org/starttls-everywhere/policy.json.asc
gpg --recv-key B693F33372E965D76D55368616EEA65D03326C9D
gpg --trusted-key 842AEA40C5BCD6E1 --verify policy.json.asc
```

Our sample [update_and_verify.sh script](https://github.com/EFForg/starttls-everywhere/blob/master/scripts/update_and_verify.sh) does the same. If you are actively using the list, **you must fetch updates at least once every 48 hours**. We provide [a sample cronjob](https://github.com/EFForg/starttls-everywhere/blob/master/scripts/starttls-policy.cron.d) to do this.

Every policy JSON has an expiry date in the top-level configuration, after which we cannot guarantee deliverability if you are using the expired list.

#### Behavior

A domain's policy, `enforce` or `testing`, asks that relays which connect to that domain's MX server and cannot initiate a TLS connection perform different behaviors depending on the policy (e.g. reporting what went wrong to the target domain for `testing`, and additionally aborting the connection for `enforce`). That is the behavior specified by [SMTP MTA Strict Transport Security (MTA-STS)](https://tools.ietf.org/html/rfc8461), an upcoming protocol which this Policy List aims to complement by providing an alternative method for advertising a mail server’s security policy.

#### Tooling

Our [starttls-policy](https://github.com/EFForg/starttls-everywhere/tree/master/starttls-policy) Python package can fetch updates to and iterate over the existing list. If you use Postfix, we provide utilities to transform the policy list into configuration parameters that Postfix understands.

We welcome [contributions](https://github.com/EFForg/starttls-everywhere) for different MTAs!

## Submitting your domain to the list

### The process

 1. Submit [this form](https://starttls-everywhere.org/add-domain).
 2. Check your postmaster@ inbox to confirm the addition request.

Now, if your domain has a valid [MTA-STS](https://tools.ietf.org/html/rfc8461) policy up, you're done! Go celebrate. Otherwise:

 3. In about a month, your postmaster@ address will receive an email prompting you to switch from "testing" mode to "enforce" mode. Reply affirmatively once you'd like to turn on strict validation for your domain.

If anything goes wrong between each of these steps, you'll receive an automated email in your postmaster@ inbox with steps to remedy.

More details below about the process, if you're curious:

#### The form

When submitting your domain to the list through [this form](https://starttls-everywhere.org/add-domain), you must provide and verify:

 * A contact email used by STARTTLS Everywhere to notify the mailserver administrator of any deliverablity concerns as well as major updates to the STARTTLS Everywhere project. (We won't use this email for any other purpose).
 * A list of the expected MX hostnames for your server. At least one of the names on each mailserver's certificate should match one of these patterns.
    * These can be a suffix, like `.eff.org`, or a fully-qualified domain name, like `mx.eff.org`. Suffixes will only match one subdomain label, so `.eff.org` would match names `*.eff.org` and `mx.eff.org`, but not `good.mx.eff.org` or `*.mx.eff.org`.

#### Automated validation

For your email domain to be eligible for addition to the STARTTLS policy list, the requirements are that your domain:

 * Supports STARTTLS (TLS v1.2 and above)
 * Supplied MX hostnames are valid (DNS lookup from this perspective resolves to hostnames that match the given patterns).
 * Provides a valid certificate. Validity means:
    * The certificate's Common Name or a subjectAltName should match the server's MX hostname.
    * The certificate is unexpired.
    * There is a valid chain from the certificate to a root included in [Mozilla's trust store](https://wiki.mozilla.org/CA/Included_Certificates) (available as Debian package [ca-certificates](https://packages.debian.org/sid/ca-certificates)).

(Note: you can obtain a valid certificate for free via [Certbot](https://certbot.eff.org), a client for the [Let's Encrypt](https://letsencrypt.org) certificate authority.)

Before adding a domain to the list, we continue to perform validation against the mailserver for at least one week. If it fails at any point, **it must be resubmitted.**

With that in mind, you can [queue your mail domain](https://starttls-everywhere.org/add-domain) for the STARTTLS policy list. Alternatively, you can send an email to [starttls-policy@eff.org](mailto:starttls-policy@eff.org) or [submit a pull request](https://github.com/EFForg/starttls-everywhere) to add your domain, though these other channels may take longer for your domain to be submitted.

#### Which mode: `testing` or `enforce`?

`testing` mode will allow you to test things out, and gives you a period of time to receive server misconfiguration reports in case you have any. However, there are little security benefits to this.

`enforce` mode gives you the security benefits by enforcing the specified security policy. That is, `enforce` mode asks other mailservers to keep email queued unless they can connect to a mailserver over authenticated TLS whose hostname matches one that appears in the `mxs` policy.

If your domain has a valid MTA-STS policy up, we'll use the mode indicated in your policy file.

If your domain doesn't have a valid MTA-STS policy, your domain will be soft-queued in "testing" mode. Once your email domain has been on the list for at least two weeks, you can request it be upgraded to "enforce"-- send `starttls-policy@eff.org` an email.

#### Continued requirements

Failure to continue meeting these requirements could result in deliverability issues to your mailserver, from any mail clients configured to use the STARTTLS policy list.

We continue to validate all the domains on the list daily. If we notice any oddities, we will notify the contact email associated with the policy submission and urge you to either update or remove your policy.

## Updating or removing your policy entry on the list

If you're migrating email hosting, you'll need to update the MX hostnames associated with your domain's policy. Contact us beforehand so we can minimize the deliverability impact. If we notice that you have migrated domains, we will reach out to you through a contact email that you provide, and the postmaster@ address.

If you'd like to request removal from the list, or an update to your policy entry (or associated contact email), contact us at [starttls-policy@eff.org](mailto:starttls-policy@eff.org)

## Adding pins to the list

We also accept requests to pin intermediate certificate public keys. Although this option gives operators flexibility in trust, key pinning carries higher risks of breakage and is more difficult to do correctly. As such, these requests will be judged on a case-by-case basis.

This basis will be determined by the site operator's understanding of the following:

   * How to generate and use a leaf key backup pin.
   * Changing to a certificate chain outside the pinset will break deliverability to your mailserver.
   * Removing a preloaded pin may take as long as a week.

We will require a form of DNS validation (to submit a TXT record for the email domain with a challenge of our choice) in order to validate that the pinning request comes from the site operator.
To pin your mailserver, contact us with more information about your request at [starttls-policy@eff.org](mailto:starttls-policy@eff.org).
