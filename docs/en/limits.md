# Security and limits

Rheic is alpha software. The local VM design uses containerd, a patched nerdbox shim, libkrun, a pinned guest kernel and rootfs, and a policy-enabled gateway. `rsbx` speaks to the local daemon. A successful CLI command alone does not prove guest isolation or policy enforcement.

| Area | Current evidence | Open gate |
|---|---|---|
| macOS ARM64 VM | Local create/start/exec/stop and basic live guest boot recorded | Complete Docker workload and network-policy parity |
| Linux ARM64 | Guest task booted in an owned nested KVM Lima VM | Native Linux host and rootless qualification |
| Native bundle | Exact file inventory, archive checksums, basic VM boot | Independent provenance for native archives; macOS notarization |
| Windows WHP | No implementation | Build and live runtime validation |
| Cloud | No Rheic cloud backend | Docker `--cloud`, `move`, `ttl`, `volume` |
| Security review | Internal tests and CI exist | Independent external review not performed |

The CLI's default network profile is `allow-all`. Select a narrower profile when needed and verify the actual gateway configuration. Never infer network enforcement from help text or a state-only daemon. Direct workspaces expose host files to the guest; `--clone` uses a private copy. Secrets and host hooks need explicit trust and scoped environment handling.

The internal product PLAN tracks detailed evidence and unresolved gates. The [CLI comparison](comparison.md) summarizes public findings; this site marks untested behavior as open.
