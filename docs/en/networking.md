# Network access and ports

Network access is controlled by the daemon and policy gateway. New sandboxes default to the `allow-all` egress profile: TCP and UDP to `0.0.0.0/0`, matching the Docker `sbx` baseline. Explicit deny rules still win over allows, organization deny rules keep precedence over local rules, and every fail-closed control is unchanged. `deny-all` remains selectable, and a sandbox using it cannot reach the network until a rule permits it.

## Default profile and rules {#default-profile}

Select default-deny for one sandbox or for the global default:

```sh
rsbx run --policy-profile deny-all shell .
rsbx policy init deny-all
rsbx settings set policy.profile deny-all
```

`allow-all`, `balanced`, and `deny-all` are the effective profiles; `sbx-compat` is accepted as an alias for `allow-all`. The resolved profile is stored with the sandbox and shown by the `rsbx ls` table and `rsbx get`.

Create-time rules accept IPv4 CIDRs with an optional port. TCP is the default; prefix a rule with `udp:` for UDP:

```sh
rsbx run --allow-network 203.0.113.8/32:443 shell .
rsbx run --allow-network udp:203.0.113.53/32:53 shell .
rsbx run --deny-network 203.0.113.0/24 shell .
```

Use documentation-only example addresses above; replace them with destinations the task actually needs. Explicit deny rules take priority over allows. Global and sandbox rules are shown by `rsbx policy ls`.

Domain rules require a configured DNS upstream and a compatible patched gateway. Domain-aware TLS enforcement remains experimental; encrypted ClientHello, domain-only UDP, and overlapping direct-IP rules have documented restrictions. Do not treat a domain allow as a general DNS or HTTP filter.

## HTTP conditions {#http-conditions}

The gateway policy layer can carry HTTP conditions on a network rule:

- `method`: an exact, case-insensitive list of `GET`, `HEAD`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `CONNECT`, or `TRACE`; `ANY` matches every method while keeping the rule HTTP-only.
- `path`: an absolute path glob. `*` matches inside one segment, `?` matches one character, character classes are supported, and a whole `**` segment matches zero or more segments.
- `query`: ordered `name=value` requirements where the value may use the same single-segment glob syntax. Every listed parameter must be present; extra parameters are allowed.

HTTP conditions are evaluated on the bounded request head, never the body. A conditional rule only matches an HTTP request that satisfies every condition; a UDP flow or a request with no HTTP metadata never matches it. An unevaluable condition does not match and never falls back to matching everything. Deny rules are evaluated before allow rules.

An allow and deny rule with the same selector in the same scope are rejected with a typed conflict error that names both rules. Duplicate opposite rules are refused at mutation time rather than left for the datapath to resolve.

The gateway policy layer implements, validates, and renders these conditions, but the local `rsbx` policy surface does not expose `method`, `path`, or `query` fields yet. `rsbx run` and `rsbx policy` therefore cannot author a rule with HTTP conditions in this alpha. Live `gvproxy` datapath enforcement of HTTP conditions and CONNECT is also unverified, so an HTTP rule is not evidence of a live packet filter.

## Publish a service

Published guest ports bind to host loopback. They are not exposed to other machines on the network:

```sh
rsbx run --publish 127.0.0.1:8080:3000 shell .
rsbx ports my-sandbox
```

The protocol can be TCP or UDP. IPv4 and IPv6 loopback forms are available on supported gateway builds. A guest listener must bind to an address reachable from the sandbox interface, commonly `0.0.0.0`.

Port publishing allows host-to-guest connections. It does not grant outbound access from the guest, and with `deny-all` the guest still needs egress rules. Configure those separately.

## Inspect and change policy

```sh
rsbx policy ls my-sandbox
rsbx policy allow network --sandbox my-sandbox 203.0.113.8/32:443
rsbx policy deny network --sandbox my-sandbox 203.0.113.8/32:443
rsbx policy check network --sandbox my-sandbox 203.0.113.8:443
```

The local `policy check` command evaluates stored rules. It is not a live query to the gateway and does not prove that a packet will pass. `rsbx policy ls --json` emits the sbx `{"rules":[...]}` schema; `rsbx policy org` shows enforced and advisory organization rules.

## Limits

Gateway validation remains platform- and build-specific. Complete IPv6 egress, QUIC/DoH bypass coverage, live HTTP-condition enforcement, and independent security review are not established. See the [security guide](security.md) for the current scope.
