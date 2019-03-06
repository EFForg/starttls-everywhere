# STARTTLS Policy List Validation

For information about configuration of sending mailservers and using the list to validate TLS configurations, please see [USAGE.md](USAGE.md) instead.

## MTA-STS

In order to be preloaded onto the STARTTLS policy list, the easiest way to do and maintain this is to have a valid MTA-STS record up for a max-age of at least half a year (10886400).

To change your entry on the list, you can serve a valid MTA-STS record with your new expected policy.

To be removed from the list, you can serve a valid MTA-STS record with `mode: none`.

## Manual addition

If you don't have an MTA-STS file up, For your email domain to be eligible for addition to the STARTTLS policy list, the requirements are that your domain:

 * Supports STARTTLS (as a receiving mailserver)
 * Supplied MX hostnames are valid (DNS lookup from this perspective resolves to hostnames that match the given patterns).
 * Provides a valid PKI certificate. Validity is defined as in [RFC 3280](https://tools.ietf.org/html/rfc3280#section-6). To clarify:
    * The certificate's Common Name or a subjectAltName should match the server's MX hostname.
    * There is a valid chain, served by the server, from the certificate to a root included in [Mozilla's trust store](https://wiki.mozilla.org/CA/Included_Certificates) (available as Debian package [ca-certificates](https://packages.debian.org/sid/ca-certificates)).
    * The certificate is not expired or revoked.

(Note: you can obtain a valid certificate for free via [Certbot](https://certbot.eff.org), a client for the [Let's Encrypt](https://letsencrypt.org) certificate authority.)

Before adding a domain to the list, we continue to perform validation against the mailserver for at least one week. If it fails at any point, **it must be resubmitted.**

With that in mind, you can [queue your mail domain](https://starttls-everywhere.org/add-domain) for the STARTTLS policy list. Alternatively, you can send an email to [starttls-policy@eff.org](mailto:starttls-policy@eff.org) or [submit a pull request](https://github.com/EFForg/starttls-everywhere) to add your domain, though these other channels may take longer for your domain to be submitted.

#### Continued requirements

Failure to continue meeting these requirements could result in deliverability issues to your mailserver, from any mail clients configured to use the STARTTLS policy list.

We continue to validate all the domains on the list daily. If we notice any oddities, we will notify the contact email associated with the policy submission and urge you to either update or remove your policy.

## Manually removing your policy entry from the list

If you're migrating email hosting, you'll need to update the MX hostnames associated with your domain's policy. Contact us beforehand so we can minimize the deliverability impact and remove your policy from the list-- we may also issue a challenge, solvable over DNS or HTTPS, in order to validate your intentions (more details in the threat modelling section). If we notice that you have migrated domains, we will reach out to you through a contact email that you provide, and the postmaster@ address.

If you'd like to request removal from the list, or an update to your policy entry (or associated contact email), contact us at [starttls-policy@eff.org](mailto:starttls-policy@eff.org)

## Threat modelling and security considerations

### DNS forgery

An attacker with the ability to forge DNS requests to a sending mailserver for a particular receiving mailserver might provide fake MX records for the receiving mailserver, causing the sender to direct its mail towards a malicious server. This is thwarted if the sender validates against the policy list and discovers that the receiving server uses a different set of hostnames.

This type of attacker may try and induce a removal and re-addition of a policy to the list. To do this, they might need to induce a validating CA to misissue a certificate, or maintain a machine-in-the-middle position on our validation server for several weeks, and against our notification email server, which will send updates to the policy's email contact (also unknown to the attacker, and could be hosted on a different server) about these attempts.

### TCP on-path attacker

Normally, a regular on-path attacker might simply downgrade TLS. A more sophisticated one might perform a certificate man-in-the-middle. In either case, this is thwarted if the sender is validating against the policy list and discovers that the receiving server should support TLS with a valid certificate.

This type of attacker may try and induce removal of that receiving server from the policy list. To prevent this, we'll issue a DNS challenge to validate any policy list removal.

### CA compromise or induced misissuance

When a valid MTA-STS record is discovered, the STARTTLS policy list cannot necessarily provide a higher degree of security, since we also validate TLS policies from our own network position. Thus, MTA-STS policies should take precedence over the STARTTLS policy list. 

This means that we do assume CA compromise or misissuance is more difficult (in terms of cost, risk, and detectability thanks to Certificate Transparency, or CT) than performing a single DNS on-path attack or forgery, and than performing a TCP on-path attack. However, it is possible, with a temporary DNS machine-in-the-middle position (perhaps due to BGP hijacking) with respect to an automated CA like Let's Encrypt, to induce certificate misissuance. 

Some of these judgments depend on an adversary's relative network perspective to the target mailserver and various automated CAs. Regardless, inducing misissuance is at least detectable if a domain owner is [monitoring CT logs](), and may require extra effort (depending on network perspective) in addition to having a machine-in-the-middle DNS position targeted towards a particular mailserver. Hopefully, with [multi-perspective validation](https://letsencrypt.org/upcoming-features/) on the horizon for Let's Encrypt, the bar could be raised even higher for an attacker to induce misissuance.

