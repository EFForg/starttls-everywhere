# Policy rule configuration format

The TLS policy file is a `json` file which conforms to the following specification. These fields draw inspiration from the [MTA-STS policy file format](https://tools.ietf.org/html/rfc8461) as well as [Chromium's HSTS Preload List](https://hstspreload.org/).
The basic file format will be JSON. Example:

```
{
  "timestamp": "2014-06-06T14:30:16+00:00",
  "author": "Electronic Frontier Foundation https://eff.org",
  "expires": "2014-06-06T14:30:16+00:00",
  "version": "0.1",
  "policy-aliases": {
    "gmail": {
      "mode": "testing",
      "mxs": [".mail.google.com"],
    }
  },
  "policies": {
    "yahoo.com": {
      "mode": "enforce",
      "mxs": [".yahoodns.net"]
     },
    "eff.org": {
      "mode": "enforce",
      "mxs": [".eff.org"]
    },
    "gmail.com": {
      "policy-alias": "gmail"
    },
    "example.com": {
      "mode": "testing",
      "mxs": ["mail.example.com", ".example.net"]
    },
  },
}
```

At a high level, senders will expect the following for recipient domains:
 - 1. Email domain resolves to an MX hostname which matches an entry in `mxs`
 - 2. Provides a valid certificate. Validity means:
    - a. The CN or DNS entry under subjectAltName matches an appropriate hostname.
    - b. The certificate is unexpired.
    - c. There is a valid chain from the certificate to a root included in [Mozilla's trust store](https://www.mozilla.org/en-US/about/governance/policies/security-group/certs/included/) (available as [Debian package ca-certificates](https://packages.debian.org/sid/ca-certificates)).
 - 3. Successfully negotiates a TLS session (>= TLS 1.2).

A user of this file format may choose to override individual domain policies. For instance, the EFF might provide an overall configuration covering major mail providers, and another organization might produce an overlay for mail providers in a specific country.

Before adding a policy to this list, we validate that the email domain conforms to the policy, as above.

Note that there is no inline signature field. The configuration file should be distributed with authentication using an offline signing key, generated using `gpg --clearsign`. Config-generator should validate the signature against a known GPG public key before extracting. The public key is part of the permanent system configuration, like the fetch URL.

### Top-level fields
#### expires
When this configuration file expires, in UTC. Can be in epoch seconds from 00:00:00 UTC on 1 January 1970, or a string `yyyy-MM-dd'T'HH:mm:ssZZZZ`. If the file has ceased being regularly updated for any reason, and the policy file has expired, the MTA should fall-back to opportunistic TLS for e-mail delivery, and the system operator should be alerted.

#### timestamp
When this configuration file was distributed/fetched, in UTC. Can be in epoch seconds from 00:00:00 UTC on 1 January 1970, or a string `yyyy-MM-dd'T'HH:mm:ssZZZZ`. This field will be monotonically increasing for every update to the policy file. When updating this policy file, should validate that the timestamp is greater than or equal to the existing one.

#### policy-aliases
A mapping of alias names onto a policy. Domains in the `policies` field can refer to policies defined in this object.

#### policies
A mapping of mail domains (the part of an address after the "@") onto a "policy". Matching of mail domains is on an exact-match basis. For instance, `eff.org` would be listed separately from `lists.eff.org`. Fields in this policy specify security requirements that should be applied when connecting to any MTA server for a given mail domain. If the `mode` is `testing`, then the sender should not stop mail delivery on policy failures, but should produce logging information.

#### version
Version of the configuration file.

### Policy fields
Every field in `policies` maps to a policy object. A policy object can have the following fields:

#### policy-alias

If set, other fields are ignored. This value should be a key in the upper-level "policy-aliases" configuration object. The policy for this domain will be configured as the denoted policy in the "policy-aliases" object.

#### mode
Default: `testing` (required)

Either `testing` or `enforce`. If `testing` is set, then the recipient expects any failure in TLS negotiation to be reported via a mechanism such as TLSRPT, but the message is still sent over the insecure communication.

#### mxs

A list of the expected MX hostnames for your server. At least one of the names on each mailserver's certificate should match one of these patterns. The pattern can be a suffix, like `.eff.org`, or a fully-qualified domain name, like `mx.eff.org`. Suffixes will only match one subdomain label, so `.eff.org` would match names `*.eff.org` and `mx.eff.org`, but not `good.mx.eff.org` or `*.mx.eff.org`.

