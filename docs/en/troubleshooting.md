# Troubleshooting

Start with the exact binary version and its built-in help:

```sh
rsbx --help
rsbx diagnose
sandboxesd --help
```

`rsbx diagnose` prints a sectioned report (installation, platform, storage, connection) of individually graded checks with a pass/fail/warning/skip summary and exits non-zero when a check fails. `--json` emits the flat sbx report (`version`, `checks[]`, `summary`), and `--format github-issue` produces a Markdown issue body. `rsbx policy log` shows the gateway audit decisions (allowed/denied destinations with the matching rule) recorded in the daemon run directory.

## The CLI cannot connect

Point the CLI at the same local socket used by the daemon:

```sh
rsbx --socket "$HOME/.sandboxes/sandboxesd.sock" ls
```

Check that the daemon is running and that your account can access the socket. `SANDBOXES_SOCKET` can provide the default socket path. Use `rsbx daemon status` to inspect the live endpoint, version, API version, and log path. Do not replace an unknown socket or state directory.

## The daemon will not stop

`rsbx daemon stop` only signals a daemon whose identity it can prove. A daemon started outside `rsbx daemon start` is stopped when its identity is proven from the live socket peer. If that cannot be proven, stop refuses without signaling and prints an actionable message. Inspect the process that owns the socket, stop it manually with `SIGTERM`, and verify the endpoint before removing state. On platforms that cannot discover the socket peer, the command decides from the control record. Stale sockets and control records must be verified, not deleted blindly.

## A sandbox does not start

The state-only fallback in the [quick start](quickstart.md) starts the control plane but does not configure a VM backend, so that command alone will not boot a VM. Guest execution also requires compatible containerd, runtime, guest image, shim, and helper artifacts configured for the platform. VM-backed CLI lifecycle and exec checks passed live acceptance on macOS ARM64; this does not validate the full agent workflow. Windows WHP is not implemented, and Linux KVM is not qualified. Check the [requirements](requirements.md) and [architecture](architecture.md) for the platform-specific setup and current limits. `rsbx start` fails closed when the daemon has no runtime backend and restores the sandbox to stopped.

## Network access fails

New sandboxes use the `allow-all` egress profile by default. If a sandbox was created with `deny-all`, or an explicit deny rule matches, check the sandbox policy, configured gateway, and DNS upstream. Add only the required destination rule. `rsbx policy check` evaluates stored policy inputs; it does not verify live packet enforcement by the gateway. `rsbx policy log` prints recent gateway audit decisions with the matched rule; `rsbx policy inspect RULE_ID|SANDBOX` shows one rule or sandbox policy in detail. See [Network and ports](networking.md).

## Docker sign-in worked, but guest pulls fail

Docker account authorization is stored on the host. Guest registry credential brokering is experimental and has not passed live VM acceptance. See [Docker](docker.md).

## A name is already tied to another workspace

Use a new sandbox name for a different workspace, or inspect the existing sandbox with `rsbx get NAME`. Do not assume reusing a name switches the mounted host directory.

## Removing a sandbox did not remove host files

Sandbox removal does not delete the host workspace. Review and remove project files yourself after confirming their location; Gyrel does not own arbitrary host directories.

For an unresolved issue, capture `rsbx diagnose` output after checking it for local paths or sensitive metadata, and include the exact module versions and platform. Never attach credentials or unredacted secrets.
