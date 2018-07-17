# Policy rule configuration format

The TLS policy file is a `json` file which conforms to the following specification. These fields are draw inspiration from the [MTA-STS policy file format](https://tools.ietf.org/html/draft-ietf-uta-mta-sts) as well as [Chromium's HSTS Preload List](https://src.chromium.org/chrome/trunk/src/net/http/transport_security_state_static.json) (and the associated CA Pinning list).
The basic file format will be JSON. Example:

```
{
  "timestamp": "2014-06-06T14:30:16+00:00",
  "author": "Electronic Frontier Foundation https://eff.org",
  "expires": "2014-06-06T14:30:16+00:00",
  "version": "0.1",
  "pinsets": {
    "eff": {
      "static-spki-hashes": [
        "sha1/5R0zeLx7EWRxqw6HRlgCRxNLHDo=",
        "sha1/YlrkMlC6C4SJRZSVyRvnvoJ+8eM=",
      ]
    }
   },
  "policy-aliases": {
    "gmail": {
      "mode": "testing",
      "report": ["https://google.com/post/reports/here"],
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
      "pin": "eff",
      "mxs": [".eff.org"]
    },
    "gmail.com": {
      "policy-alias": "gmail"
    },
    "example.com": {
      "mode": "testing",
      "mta-sts": true,
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
    - d. If `pins` is set, then one of the `static_spki_hashes` SPKIs in the pinset is found in the chain.
 - 3. Successfully negotiates a TLS session.
    - Includes honoring `min-tls-version` field.

A user of this file format may choose to override individual domain policies. For instance, the EFF might provide an overall configuration covering major mail providers, and another organization might produce an overlay for mail providers in a specific country.

Before adding a policy to this list, we validate:
 - 1. The email domain conforms to the policy, as above.
 - 2. Any specified reporting endpoints via `report` are active (POST succeeds for https endpoints, and mailto: addresses don't bounce)

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

#### pinsets
Maps a unique pinset name to a list of accepted pins. For a given pinset, a certificate is accepted if at least one of the `static_spki_hashes` SPKIs is found in the chain.

#### version
Version of the configuration file.

### Pinset fields
#### static-spki-hashes
The set of allowed SPKIs hashes.

### Policy fields
Every field in `tls-policies` maps to a policy object. A policy object can have the following fields:

#### policy-alias

If set, other fields are ignored. This value should be a key in the upper-level "policy-aliases" configuration object. The policy for this domain will be configured as the denoted policy in the "policy-aliases" object.

#### min-tls-version
Default: `TLSv1.2`

The minimum TLS version expected from this domain. Sending mail to domains under this policy should fail if the sending MTA cannot negotiate a TLS version equal to or greater than the listed version. Valid values are `TLSv1`, `TLSv1.1`, and `TLSv1.2`.

#### mode
Default: `testing` (required)

Either `testing` or `enforce`. If `testing` is set, then any failure in TLS negotiation is logged and reported, but the message is sent over the insecure communication.

#### mta-sts
Default: `false`

If set, then senders should expect this recipient domain to support [MTA-STS](https://tools.ietf.org/html/draft-ietf-uta-mta-sts).

#### mxs

A list of hostnames that the recipient email server's certificates could be valid for. If the server's certificate matches no entry in `mxs`, the MTA should fail delivery or log an advisory failure, according to `mode`. Entries in the `mxs` list can either be a suffix indicated by a leading dot `.example.net` or a fully qualified domain name `mail.example.com`. Arbitrarily deep subdomains can match a particular suffix. For instance, `mta7.am0.yahoodns.net` would match `.yahoodns.net`.

#### pin

Should match a key of `pinsets` in the higher-level config. For a given pinset, a certificate for this mail domain should be accepted if at least one of the `static_spki_hashes` SPKIs is found in the trust chain.

#### report

Endpoints to report errors to if TLS negotiation fails according to a particular policy. Reports should be aggregated and sent in the format specified by [TLSRPT](https://tools.ietf.org/html/draft-ietf-uta-smtp-tlsrpt). These URIs should be `https` or `mailto` endpoints, and aggregated reports should be `POST`ed to the specified HTTPS URL or mailed to the appropriate address.
