# Security model

Gyrel is designed to keep agent workloads inside isolated microVM sandboxes and to keep host credentials under host control. This is an implementation direction, not a blanket security certification. Gyrel is alpha software.

## Trust boundaries

- The local CLI talks to a local daemon over a permission-restricted socket.
- The daemon owns sandbox metadata and coordinates the runtime.
- The VM runtime separates guest workloads from host processes.
- New sandboxes use the `allow-all` egress profile by default, matching Docker `sbx`. Explicit deny rules, organization deny precedence, and every fail-closed control still bound network access; `deny-all` remains selectable.
- Provider credentials are stored in the native host credential vault. They are not intended to enter sandbox metadata, SQLite, or logs.

## Safe operating practices

- Review workspace contents before sharing a writable workspace with an agent. Use `:ro` for read-only inputs.
- The default egress profile is permissive. Add deny rules or start the sandbox with `--policy-profile deny-all` when a task does not need network access.
- Do not put credentials in command arguments or ordinary environment overrides. Prefer the host credential-vault commands where the feature is supported.
- Treat host hooks, MCP stdio servers, lifecycle commands, and writable mounts as code running with the permissions of their host process. Use them only with explicit approval and a constrained environment.
- Use isolated test directories and uniquely named sandboxes for experiments. Remove only resources created by your own run.

## Current limitations

Gyrel does not yet claim complete Docker Sandboxes parity or a production security boundary. A VM-backed lifecycle has passed limited acceptance on macOS ARM64. A Linux ARM64 guest task also survived managed-containerd detach/reattach in an Ubuntu Lima/QEMU VM with nested KVM on macOS; native Linux host and rootless operation remain unqualified. Windows WHP is not implemented. Cloud commands (`move`, `ttl`, `volume`) are out of scope for the local alpha.

The opt-in `--docker` profile can start a Docker daemon inside the guest, but nested workload operations such as `docker run`, `docker load`, `docker build`, and Compose remain blocked in the current runtime by guest `unshare` restrictions. This limitation does not mean the VM itself fails to start. The host Docker socket is not mounted.

The service-secret proxy supports multiple service routes per sandbox, but fault testing and independent security review remain open. Registry and some agent paths are incomplete or fail closed. HTTP policy conditions are modelled and validated, but live `gvproxy` HTTP datapath enforcement is unverified. OAuth expiry and refresh lifecycle, host crash and power-loss cleanup, complete network bypass coverage, and an independent external security review remain open work. The managed Linux launcher currently fails closed without `CAP_SYS_ADMIN`; that confirms rootless refusal, not rootless workload support.

VM-backed lifecycle and exec checks passed on macOS ARM64. They do not qualify complete agent sessions, other platforms, or every network path. Read the [requirements](requirements.md), [architecture](architecture.md), [workspace](workspaces.md), [network](networking.md), and [credentials](credentials.md) guides for tested scope and component-specific limits.

See the [Docker guide](docker.md) for the difference between host account sign-in, registry access, and Docker Engine inside a sandbox.

This page summarizes the security model and its known limitations. A missing validation result means unknown or unverified, not safe by assumption.
