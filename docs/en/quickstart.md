# Quick start

This guide installs the released Sandboxes alpha by Gyrel and boots a real microVM on macOS ARM64. The microVM path is the primary path: the launcher starts the pinned containerd, the daemon drives the nerdbox shim and libkrun, and `rsbx run shell .` creates or reuses the sandbox, starts it, and attaches the guest shell. State-only mode is a labelled fallback for hosts without the runtime assets and does not boot a VM.

The published alpha is CLI `rsbx` v0.0.74, daemon `sandboxesd` v0.0.98, and local API contract 0.0.38, assembled as one verified alpha bundle with pinned runtime assets and artifact digests. Binaries ship with `SHA256SUMS`; the bundle launcher verifies every runtime artifact by SHA-256 before each VM launch and refuses unverified bytes. Live acceptance on macOS ARM64 covers the full VM lifecycle, workspaces, `cp`, port publishing, template save/load with live roundtrip, host vault credentials with custom secrets and the approval flow, `mcp` registration with approval challenges, kit validation with the daemon policy, skills, the TUI event panels, and the IPv6 and QUIC opt-in matrices. It does not qualify Windows, native Linux or rootless hosts, or cloud commands. Windows WHP is not implemented, cloud commands are out of scope, and no independent external security review has been completed.

## 1. Download and verify the alpha bundle

The bundle contains the CLI, the daemon, the pinned runtime (containerd with patches, the nerdbox shim, gvproxy, libkrun, kernel and guest rootfs), the digest file, and the managed launcher. Download `rheic-sandboxes-alpha-darwin-arm64-r4.tar.gz` and its `.sha256` from the [project releases](https://github.com/gyrel/sandboxes/releases) — that r4 bundle was published under the previous brand, so its archive keeps the `rheic-` file names — then:

```sh
shasum -a 256 -c rheic-sandboxes-alpha-darwin-arm64-r4.tar.gz.sha256
tar -xzf rheic-sandboxes-alpha-darwin-arm64-r4.tar.gz
cd rheic-sandboxes-alpha-darwin-arm64
shasum -a 256 -c SHA256SUMS
```

The host needs Homebrew `e2fsprogs` (`brew install e2fsprogs`) for `mkfs.ext4`; the launcher locates it and fails fast with that hint when it is missing.

## 2. Install the CLI and start the managed daemon

```sh
mkdir -p ~/.local/bin
install -m 0755 bin/rsbx ~/.local/bin/rsbx
bin/gyreld-launch.sh &
~/.local/bin/rsbx daemon status   # running, with version and API contract
```

The launcher starts containerd on its own, points the daemon at the bundled runtime, and enables per-launch artifact digest verification (`--artifact-digests` plus the pinned `--runtime-artifact` set). Never mix binaries from different releases: the published set is CLI v0.0.74 with daemon v0.0.98 and API contract 0.0.38. Do not point the daemon at a socket or state directory owned by another installation. The r4 bundle published under the previous brand ships its launcher as `bin/rheicd-launch.sh`; Gyrel bundles from r5 on use `bin/gyreld-launch.sh`, so run the launcher name present in the extracted `bin/` directory.

For development against an existing local runtime you may instead run `bin/sandboxesd` with explicit flags (`--ctr`, `--gvproxy`, `--proxy-helper`); state-only mode is documented below. The escape hatch `--allow-unmanaged-runtime` exists but is not the supported alpha path: prefer the launcher so digests are enforced.

## 3. Run a microVM

```sh
cd /path/to/project
rsbx run shell .
```

`run` creates or reuses the sandbox, starts it, and attaches the guest shell. The current directory is the default workspace, mounted in the guest at the same absolute path. `--detach` returns after startup, and agent arguments follow `--`.

```sh
rsbx ls
rsbx ls --json
```

Both commands use the default socket `$HOME/.sandboxes/sandboxesd.sock` (the launcher honours `GYREL_STATE_DIR`; the legacy `RHEIC_STATE_DIR` is still honored but logs a deprecation warning — rename it to `GYREL_STATE_DIR`). If you started the daemon elsewhere, pass `--socket PATH` or set `SANDBOXES_SOCKET`. Use `rsbx stop`, `rsbx rm`, and `rsbx prune` for the rest of the lifecycle; a stopped sandbox restarts automatically on `exec`.

## 4. Try the core surfaces

```sh
rsbx ports NAME                          # published ports
rsbx cp ./file.txt NAME:/tmp/file.txt    # files both ways
rsbx template save NAME mytpl && rsbx template ls
rsbx secret ls && rsbx secret set-custom --host api.example.com --env API_KEY
rsbx policy check network api.openai.com --method GET   # evaluate one request against stored rules
rsbx kit validate ./my-kit --offline
rsbx mcp add docs --url https://mcp.example.com/mcp   # registration approval challenge
rsbx policy approval ls                  # pending consent requests
rsbx tui                                 # dashboard with live events
```

More end-to-end scenarios with exact expected output are in [user cases](user-cases.md).

## State-only fallback (no VM)

State-only mode is a fallback for a machine that does not have the runtime assets yet, or for inspecting the local control plane without a guest. It never boots a VM:

```sh
sandboxesd --state "$HOME/.sandboxes-gyrel-check" --socket "$HOME/.sandboxes-gyrel-check/sandboxesd.sock"

rsbx --socket "$HOME/.sandboxes-gyrel-check/sandboxesd.sock" ls
rsbx --socket "$HOME/.sandboxes-gyrel-check/sandboxesd.sock" diagnose
```

These commands confirm that the CLI can reach the local daemon and inspect control-plane state. They do not boot a guest, prove VM isolation, or validate an agent session.

## Limits to keep in mind

- The validated native VM path targets macOS on Apple silicon only.
- Windows WHP is not implemented. Cloud commands (`move`, `ttl`, `volume`) are out of scope for the local alpha. Nested Docker workloads inside the guest remain blocked.
- MCP server registration requires host consent; trusted OS-backed approval and interactive OAuth for remote MCP servers are not shipped yet, so approve paths fail closed. Custom-secret `--ref`/`--command` sources and L7 HTTPS interception are pending the same seams.
- No independent external security review has been completed; see the [security model](security.md).
- Docker built-in agents remain preview: image launch probes passed, but provider authentication and complete agent sessions did not. See [agents](agents.md).

## Where to go next

Read the [requirements](requirements.md) before building runtime components. See [user cases](user-cases.md) for tested scenarios, the [CLI reference](cli.md) for command syntax, [workspaces](workspaces.md), [networking](networking.md), and [credentials](credentials.md). The [Docker guide](docker.md) explains why account sign-in and guest Docker are separate. Read the [security model](security.md) before connecting a project or storing credentials.
