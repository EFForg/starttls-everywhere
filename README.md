# STARTTLS Everywhere

STARTTLS Everywhere is an initiative for upgrading the security of the email ecosystem. Several sub-projects fit underneath the general umbrella of "STARTTLS Everywhere". The name itself is a bit of a misnomer, since the original idea for the project came about in 2014, when STARTTLS support hovered around 20% across the internet. Since then we've come a long way, with [Gmail's transparency report](https://transparencyreport.google.com/safer-email/overview) citing ~90% of inbound and outbound mail are encrypted with TLS, as of 2018.

We still have a long way to go. STARTTLS (opportunistic TLS) is vulnerable to [trivial downgrade attacks](https://stomp.colorado.edu/blog/blog/2012/12/31/on-smtp-starttls-and-the-cisco-asa/) that continue to be observed across the Internet. As of 2018, a quick Zmap query for a common STARTTLS-stripping fingerprint (a banner that reads "250 XXXXXXXX" rather than "250 STARTTLS") reveals around 8 thousand hosts. This is likely an under-estimate, since active attackers can perform the stripping in a less detectable way (simply by omitting the banner, for instance, rather than replacing its body with X's).

In addition, STARTTLS is also vulnerable to TLS man-in-the-middle attacks. Mailservers currently don't validate TLS certificates, since there has only [recently](https://tools.ietf.org/html/rfc8461#section-4.2) been an attempt to standardize the certificate validation rules across the email ecosystem.

Absent DNSSEC/DANE, STARTTLS by itself thwarts purely passive eavesdroppers. However, as currently deployed, it allows either bulk or semi-targeted attacks that are very unlikely to be detected. We would like to deploy both detection and prevention for such semi-targeted attacks.

### Goals

 *  Prevent [TLS stripping](https://www.eff.org/deeplinks/2014/11/starttls-downgrade-attacks) from revealing email contents to the network, when in transit between major MTAs that support STARTTLS.
 *  Prevent active MITM attacks at the DNS, SMTP, TLS, or other layers from revealing contents to the attacker.
 *  Zero or minimal decrease to deliverability rates unless network attacks are actually occurring.
 *  Create feedback-loops on targeted attacks and bulk surveilance in an opt-in, anonymized way.

### Non-goals

 *  Prevent fully-targeted exploits of vulnerabilities on endpoints or on mail hosts.
 *  Refuse delivery on the recipient side if sender does not negotiate TLS (this may be a future project).
 *  Develop a fully-decentralized solution.
 *  Initially we are not engineering to scale to all mail domains on the Internet, though we believe this design can be scaled as required if large numbers of domains publish policies to it.

## Solution stacks

A solution needs the following things:
 - [ ] Server can advertise TLS support and MX data
 - [ ] In a non-downgrade-able way
 - [ ] Minimize deliverability impact
 - [ ] Widely deployed

### DNSSEC, DANE, and TLSRPT

With [DNSSEC](https://tools.ietf.org/html/rfc4034) and [DANE](https://tools.ietf.org/html/rfc6698) [for email](https://tools.ietf.org/html/rfc7672), mailservers can essentially publish or pin their public keys via authenticated DNS records. If a domain has DNSSEC-signed their records, the absence/presence of a DANE TLSA record indicates non-support/support for STARTTLS, respectively.

Our goals can also be accomplished through use of [DNSSEC and DANE](https://tools.ietf.org/html/rfc7672), which is a very scalable solution. DANE adoption has been slow primarily since it is dependent on upstream support for DNSSEC; operators have been very slow to roll out DNSSEC. Making DNSSEC easier to deploy and improving its deployment is, for now, outside the scope of this project, though making DANE easier to deploy may be in-scope.

The mention of [TLSRPT](https://tools.ietf.org/html/rfc8460) is due to the fact that several operators consistently deploy DNSSEC or DANE incorrectly. We want to close the misconfiguration reporting feedback loop. TLSRPT is an RFC for publishing a "reporting mechanism" to DNS. This endpoint can be an email address or a web endpoint; it is expected that senders will publish to these when failures occur, and that receivers will aggregate these reports and fix their configurations if problems arise.

 - [x] Server can advertise TLS support and MX data *(DANE TLSA records)*
 - [x] In a non-downgrade-able way *(NSEC3 for DNSSEC)*
 - [x] Minimize deliverability impact *(TLSRPT, ideally)*

### MTA-STS, Preloading, and TLSRPT

MTA-STS is a specification for mailservers to publish their TLS policy and ask senders to cache that policy, absent DNSSEC. The policy can be discovered at a `.well-known` address served over HTTPS at the email domain (for instance, [Gmail's record](https://mta-sts.gmail.com/.well-known/mta-sts.txt)). MTA-STS support is discovered through an initial DNS lookup.

There is value in deploying an intermediate solution, perhaps through [MTA-STS](https://tools.ietf.org/html/rfc8461), that does not rely on DNSSEC. This will improve the email security situation more quickly. It will also provide operational experience with authenticated SMTP over TLS that will make eventual rollout of DANE-based solutions easier.

However, MTA-STS, unlike DNSSEC + DANE, is trust-on-first-use. Since MTA-STS assumes no DNSSEC, the initial DNS query to discover MTA-STS support is downgradable. A full solution would include distributing an MTA-STS preload list via our email security database.

 - [x] Server can advertise TLS support and MX data *(MTA-STS)*
 - [x] In a non-downgrade-able way *(Preloading)*
 - [x] Minimize deliverability impact *(TLSRPT, ideally)*

## Project scope

The project scope is very large, though our development team is extremely small. The following is a list of things that we care about doing, and afterwards is a short-term timeline of the currently prioritized tasks.

If you are working next to or directly on one or more of these things, feel free to shoot us an email at starttls-everywhere@eff.org.

### Email security database (STARTTLS policy list)

 * [Usage guidelines](USAGE.md) (for configuration of sending mailservers)
 * [Validation guidelines](VALIDATION.md) (for configuration of receiving mailservers)
 * [Detailed spec](RULES.md) of list format.
 * [Submission site for adding mail domains](https://starttls-everywhere.org)
 * Maintaining and encouraging use of [starttls-policy-cli](https://github.com/EFForg/starttls-policy-cli).

### Tracking and encouraging deployment of existing standards.

 * DANE
    * Several other folks do a great job of monitoring [DANE deployment](https://mail.sys4.de/pipermail/dane-users/) and [misconfigurations](https://danefail.org/) on the internet.
 * MTA-STS
    * Encouraging MTA-STS validation support in popular MTA software.
    * Encouraging mailservers to publish their policies.
 * TLSRPT
    * Encouraging reporting support in popular MTA software.
    * Encouraging mailservers to host reporting servers/endpoints.

### Currently actively maintaining/building

 * Maintaining the [email security database](policy.json) and [submission site](https://starttls-everywhere.org)
 * Building out integrations for [starttls-policy-cli](https://github.com/EFForg/starttls-policy-cli/blob/master/README.md)
 * Encouraging MTA-STS validation support in other MTA software.

### Contributing

 * Announcements mailing list: starttls-everywhere@eff.org, https://lists.eff.org/mailman/listinfo/starttls-everywhere
 * Developer mailing list: starttls-everywhere-devs@lists.eff.org, https://lists.eff.org/mailman/listinfo/starttls-everywhere-devs
 * IRC/dev channel: TBD
 * We host a weekly development call every Thursday at 11AM Pacific Time. Shoot the mailing list an email if you're interested in joining or just sitting in.

