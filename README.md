# STARTTLS Everywhere


## Example usage

**WARNING: this is a pre-alpha codebase.  Do not run it on production
mailservers!!!**


If you have a Postfix server you're willing to endanger deliverability on, you
can try obtain a certificate with the [Let's Encrypt Python Client](https://github.com/letsencrypt/letsencrypt), note the directory it lives in below `/etc/letsencrypt/live` and then do:

```
git clone https://github.com/EFForg/starttls-everywhere
cd starttls-everywhere
# Promise you don't care if deliverability breaks on this mail server
letsencrypt-postfix/PostfixConfigGenerator.py examples/starttls-everywhere.json /etc/postfix /etc/letsencrypt/live/YOUR.DOMAIN.EXAMPLE.COM
```

This will:
* Ensure your mail server initiates STARTTLS encryption
* Install the Let's Encrypt cert in Postfix
* Enforce mandatory TLS to some major email domains
* Enforce minimum TLS versions to some major email domains

## Using the STARTTLS Policy List

To download and verify the most up-to-date version of the STARTTLS Policy List:
```
wget https://dl.eff.org/starttls-everywhere/policy.json
wget https://dl.eff.org/starttls-everywhere/policy.json.asc
gpg --recv-key B693F33372E965D76D55368616EEA65D03326C9D
gpg --trusted-key 842AEA40C5BCD6E1 --verify policy.json.asc
```

## Project status

*UPDATE (3/2018)* STARTTLS Everywhere development is re-re-starting after another hiatus.

STARTTLS Everywhere development is re-starting after a hiatus.  Initial
objectives:

* Postfix configuration generation: working pre-alpha, not yet safe
* Fully integrated Let's Encrypt client postfix plugin: in progress, not yet ready
 - Progress on these two will be tracked in [the Certbot project](https://github.com/certbot/certbot)
* Email security database: working pre-alpha, definitely not yet safe
 - We'll have an endpoint with this up at dl.eff.org in the coming weeks.
* DANE support: none yet
* DEEP support: none yet
* SMTP-STS integration: none yet
* Direct mechanisms for mail domains to request inclusion: none yet
* Failure reporting mechanisms: early progress, not yet ready
* Mechanisms for secure multi-organization signature on the policy database:
  none yet
* Support for mail servers other than Postfix: none yet

## Authors

Jacob Hoffman-Andrews <jsha@eff.org>,     
Peter Eckersley <pde@eff.org>,     
Daniel Wilcox <dmwilcox@gmail.com>,     
Aaron Zauner <azet@azet.org>
Sydney Li <sydney@eff.org>

## Mailing List

starttls-everywhere@eff.org, https://lists.eff.org/mailman/listinfo/starttls-everywhere

## Background

Most email transferred between SMTP servers (aka MTAs) is transmitted in the clear and trivially interceptable. Encryption of SMTP traffic is possible using the STARTTLS mechanism, which encrypts traffic but is vulnerable to trivial downgrade attacks.

To illustrate an easy version of this attack, suppose a network-based attacker `Mallory` notices that `Alice` has just uploaded message to her mail server. `Mallory` can inject a TCP reset (RST) packet during the mail server's next TLS negotiation with another mail server. Nearly all mail servers that implement STARTTLS do so in opportunistic mode, which means that they will retry without encryption if there is any problem with a TLS connection. So `Alice`'s message will be transmitted in the clear.

Opportunistic TLS in SMTP also extends to certificate validation. Mail servers commonly provide self-signed certificates or certificates with non-validatable hostnames, and senders commonly accept these. This means that if we say 'require TLS for this mail domain,' the domain may still be vulnerable to a man-in-the-middle using any key and certificate chosen by the attacker.

Even if senders require a valid certificate that matches the hostname of a mail host, a DNS MITM or Denial of Service is still possible. The sender, to find the correct target hostname, queries DNS for MX records on the recipient domain. Absent DNSSEC, the response can be spoofed to provide the attacker's hostname, for which the attacker holds a valid certificate.

STARTTLS by itself thwarts purely passive eavesdroppers. However, as currently deployed, it allows either bulk or semi-targeted attacks that are very unlikely to be detected. We would like to deploy both detection and prevention for such semi-targeted attacks.

## Goals

*   Prevent RST attacks from revealing email contents in transit between major MTAs that support STARTTLS.
*   Prevent MITM attacks at the DNS, SMTP, TLS, or other layers from revealing same.
*   Zero or minimal decrease to deliverability rates unless network attacks are actually occurring.
*   Create feedback-loops on targeted attacks and bulk surveilance in an opt-in, anonymized way.

## Non-goals

*   Prevent fully-targeted exploits of vulnerabilities on endpoints or on mail hosts.
*   Refuse delivery on the recipient side if sender does not negotiate TLS (this may be a future project).
*   Develop a fully-decentralized solution.
*   Initially we are not engineering to scale to all mail domains on the Internet, though we believe this design can be scaled as required if large numbers of domains publish policies to it.

## Motivating examples

*   [Unnammed mobile broadband provider overwrites STARTTLS flag and commands to
    prevent negotiating an encrypted connection](https://www.techdirt.com/articles/20141012/06344928801/revealed-isps-already-violating-net-neutrality-to-block-encryption-make-everyone-less-safe-online.shtml)
*   [Unknown party removes STARTTLS flag from all SMTP connections leaving
    Thailand](http://www.telecomasia.net/content/google-yahoo-smtp-email-severs-hit-thailand)

## Threat model

Attacker has control of routers on the path between two MTAs of interest. Attacker cannot or will not issue valid certificates for arbitrary names. Attacker cannot or will not attack endpoints. We are trying to protect confidentiality and integrity of email transmitted over SMTP between MTAs.

## Alternatives

Our goals can also be accomplished through use of [DNSSEC and DANE](http://tools.ietf.org/html/draft-ietf-dane-smtp-with-dane-10), which is certainly a more scalable solution. However, operators have been very slow to roll out DNSSEC supprt. We feel there is value in deploying an intermediate solution that does not rely on DNSSEC. This will improve the email security situation more quickly. It will also provide operational experience with authenticated SMTP over TLS that will make eventual rollout of DANE-based solutions easier.

## Interaction with MTA-STS

MTA-STS is a new IETF draft that enables senders to discover and cache a TLS policy for recipients. Recipients provide a TXT record over DNS to indicate whether they support MTA-STS, and then host a policy file at `https://mta-sts.<domain>/.well-known/mta-sts.txt`. Since MTA-STS is still TOFU, STARTTLS-Everywhere can still help bootstrap that "first use" in the event of a network attacker.

If a sender discovers a valid MTA-STS policy file for a recipient, or has a MTA-STS policy cached that is more recent than our database, then they should prefer that policy. Our database also provides the flag `mta-sts` (which will pre-empt the other policy settings) to indicate that senders should expect the recipient domain to have STS support.

If MTA-STS is more widely deployed, the role of this database will shift towards a directory of domains that support MTA-STS.

## Detailed design

Senders need to know which target hosts are known to support STARTTLS, and how to authenticate them. Since the network cannot be trusted to provide this information, it must be communicated securely out-of-band. We will provide:

  (a) a configuration file format to convey STARTTLS support for recipient domains,

  (b) Python code (in the form of various Certbot plugins) to transform (a) into configuration files for popular MTAs., and

  (c) a method to create and securely distribute files of type (a) for major email domains that that agree to be included, plus any other domains that proactively request to be included.

## File Format
Details w.r.t. the file format can be found in [`RULES.md`](RULES.md).

## Pinning and hostname verification

Like Chrome and Firefox we want to encourage pinning to a trusted root or intermediate rather than a leaf cert, to minimize spurious pinning failures when hosts rotate keys.

The other option is to automatically pin leaf certs as observed in the wild.  This would be one solution to the hostname verification and self-signed certificate problem. However, it is a non-starter. Even if we expect mail operators to auto-update configuration on a daily basis, this approach cannot add new certs until they are observed in the wild. That means that any time an operator rotates keys on a mail server, there would be a significant window of time in which the new keys would be rejected.

## Policy submission

Initially, changes to the policy file will be handled through pull requests to the `starttls-everywhere` Github repository. The updated policies will be validated manually, and if it's for a new domain, we ask for a contact e-mail in case we discover your configuration changes. If your domain fails policy validation in any way, we will not add it to the list until the issues are resolved.

In the future, we will automate this process. Operators will be able to submit mail domains to an endpoint which automatically validates the policy, and if the domain passes all checks, it will be queued for addition to the policy index. The pending changes for the policy index will be rolled into the repository on a regular (weekly or bi-weekly) basis.

Adding and removing domains from the list will be conservative. For inclusion in the list, the MTA's policy should be valid and its reporting endpoints, if specified, should be active. They must also present valid certificates and use at least TLS 1.0 in addition to properly supporting STARTTLS. We assume that if an MTA requests to be included on the list, they also somewhat care about security, and may as well do these other important things first! Since removal is also dangerous (allowing arbitrary removal can re-enable downgrade attacks), we will carefully audit and verify requests to be removed from the list manually.

## Distribution

The configuration file will be provided at a long-term maintained URL. It will be signed using a key held offline on an airgapped machine or smartcard.

Since recipient mail servers may abruptly stop supporting TLS, we will request that mail operators set up auto-updating of the configuration file, with signature verification. This allows us to minimize the delivery impact of such events. However, config-generator should not auto-update its own code, since that would amount to auto-deployment of third party code, which some operators may not wish to do.

We may choose to implement a form of immutable log along the lines of certificate transparency. This would be appealing if we chose to use this mechanism to distribute expected leaf keys as a primary authentication mechanism, but as described in "Pinning and hostname verification," that's not a viable option. Instead we will rely on the CA ecosystem to do primary authentication, so an immutable log for this system is probably overkill, engineering-wise.

## Tooling

We will provide some tooling for using and enforcing the database. For starters, we've wrapped the policy index with a Python library, `policylist`.

In particular, the Certbot plugin for Postfix, in addition to installing certificates for the e-mail domain, will provide optional enhancements to:
 - Enforce the policy DB (as sender) in Postfix configuration
    - Can specify how to fall back: if hostname mismatch or STARTTLS misconfigured.
 - Provide MTA-STS support (as receiver)
    - This can be done for any mail domain with a valid certificate, and is not just specific to Postfix. 

In the future, we plan on writing similar plugins for other popular MTAs. It should not be possible for any input JSON to cause arbitrary code execution or even any MTA config directives beyond the ones that specifically impact the decision to deliver or bounce based on TLS support. For instance, it must not be possible for any of these plugins to output a directive to forward mail from one domain to another.

These plugins will have the option to directly pull the latest config from a URL, or from a file on local disk distributed regularly from another system that has outside network access. Certbot automatically comes shipped with a cronjob which runs renewal tasks; we can bootstrap this in order to occasionally fetch a more updated version of the configuration file.

## Testing

We will create a reproducible test configuration that can be run locally and exercises each of the major cases: Enforce mode vs log mode; Enforced TLS negotiation, enforced MX hostname match, and enforced valid certificates.

Additionally, for ongoing monitoring of third-party deployments, we will create a canary mail domain that intentionally fails one of the tests but is included in the configuration file. For instance, starttls-canary.org would be listed in the configuration as requiring STARTTLS, but would not actually offer STARTTLS. Each time a mail operator commits to configuring STARTTLS Everywhere, we would request an account on their email domain from which to send automated daily email to starttls-canary.org. We should expect bounces. If such mail is successfully delivered to starttls-canary.org, that would indicate a configuration failure on the sending host, and we would manually notify the operator.

## Failure reporting and TLSRPT

For the mail operator deploying STARTTLS Everywhere, we will provide log analysis scripts that can be used out-of-the-box to monitor how many delivery failures or would-be failures are due to STARTTLS Everywhere policies. These would be designed to run in a cron job or small opt-in daemon and send notices only when STARTTLS Everywhere-related failures exceed a certain percentage for any given recipient domains. For very high-volume mail operators, it would likely be necessary to adapt the analysis scripts to their own logging and analysis infrastructure.

For recipient domains who are listed in the STARTTLS Everywhere configuration, we would provide a configuration field to specify an email address or HTTPS URL to which that sender domains could send failure information. This would provide a mechanism for recipient domains to identify problems with their TLS deployment and fix them. The reported information should not contain any personal information, including email addresses.  Example fields for failure reports: timestamps at minute granularity, target MX hostname, resolved MX IP address, failure type, certificate. Since failures are likely to come in batches, the error sending mechanism should batch them up and summarize as necessary to avoid flooding the recipient.

The format of the failure report would match TLSRPT's specifications. TLSRPT is a new IETF draft that asks receivers to advertise a reporting endpoint via a TXT record over DNS. The endpoint can either be `mailto:` or a regular URL. Senders, when encountering either a delivery failure or configuration mismatch with an MTA-STS policy, should submit an error report to this endpoint.

