# Policy rule configuration format
The TLS policy file is a `json` file which conforms to the following specification. These fields are heavily inspired by the [MTA-STS policy file format](https://tools.ietf.org/html/draft-ietf-uta-mta-sts-14).

## Top-level fields
#### expires
When this configuration file expires. Can be in epoch seconds or in UTC.

#### timestamp
When this configuration file was distributed/fetched. Can be in epoch seconds or UTC.

#### tls-policies
A mapping of domains to policies.

## Policy fields
Every field in `tls-policies` maps to a policy object. A policy object can have the following fields:

#### min-tls-version
Default: `TLSv1.2`

The minimum TLS version expected from this domain.

#### mode
Default: `testing`

Either `testing` or `enforce`. If `testing` is set, then any failure in TLS negotiation is logged and reported, but the message is sent over the insecure communication.

#### mxs
A list of domains that the receiver's certificates could be valid for.

#### tls-report
An endpoint to report errors to if TLS negotiation fails (either due to a misconfiguration or man-in-the-middle).

#### require-valid-certificate
Default: `false`

If set to true, checks to see the domain's certificate:
 
1. Is valid for a matched entry in `mxs`
2. Has not expired
3. Has a valid chain to a root certificate in `ca-certificates`

## Sample rules file

```
{
    "author": "Electronic Frontier Foundation",
    "comment": "Sample policy configuration file",
    "expires": 1404677353,
    "timestamp": 1401093333,
    "tls-policies": {
        ".valid.example-recipient.com": {
            "min-tls-version": "TLSv1.1",
            "mode": "enforce",
            "mxs": [".valid.example-recipient.com"],
            "require-valid-certificate": true,
            "tls-report": "https://tls-rpt.example-recipient.org/api/report"
        }
    }
}
```


