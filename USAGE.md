# STARTTLS Policy List Usage Guidelines

For information about configuration of receiving mailservers and addition of a receiving mailserver to the list, please see [VALIDATION.md](VALIDATION.md) instead.

## MTA-STS interoperation for sending mailservers

The ideal is for the STARTTLS policy list to act as a "preload list" for MTA-STS domains. Although there are many parallels to the web situation with HSTS and the HSTS preload list, this list is not an exact equivalent. There are a couple of edge cases to consider when implementing both MTA-STS and the policy list. This describes the expected behavior of **sending** mailservers that both validate MTA-STS and follow the policy list.

If a mailserver is able to successfully discover and validate an MTA-STS record that conflicts with a policy on the list, then the mailserver should use the MTA-STS policy. Similarly, if a mailserver has an MTA-STS record cached that conflicts with a policy on the list, then the mailserver should use the MTA-STS policy.

That is, MTA-STS should take precedence over the STARTTLS policy list. The primary benefit of the STARTTLS policy list with MTA-STS is to secure MTA-STS on first-use.


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

