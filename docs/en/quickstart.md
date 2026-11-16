# Quick start

This guide installs the released Sandboxes alpha by Rheic and boots a real microVM on macOS ARM64. The microVM path is the primary path: the daemon drives containerd, the nerdbox shim, and libkrun, and `rsbx run shell .` creates or reuses the sandbox, starts it, and attaches the guest shell. State-only mode is a labelled fallback for hosts without the runtime assets and does not boot a VM.

The published alpha is CLI `rsbx` v0.0.54, daemon `sandboxesd` v0.0.62, and local API contract 0.0.27. The binaries are published as release artifacts with `SHA256SUMS` and SLSA provenance attestations. Live acceptance on macOS ARM64 covered create, start, exec, stop, start, delete, cross-VM isolation, the IPv6 and QUIC opt-in matrices, and clone mode. It does not qualify Windows, native Linux or rootless hosts, or cloud commands. Windows WHP is not implemented, cloud commands are out of scope, and no independent external security review has been completed.

## 1. Install the alpha binaries

The installer fetches the CLI, checks its checksum, verifies the SLSA provenance attestation, and installs to `~/.local/bin`:

```sh
curl -fsSL https://raw.githubusercontent.com/rheic/sandboxes-cli/main/scripts/install.sh | sh
rsbx version    # rsbx version v0.0.54 for the current alpha
```

Download `sandboxesd` v0.0.62 for your platform from the [daemon releases](https://github.com/rheic/sandboxes-daemon/releases), then verify it against the published checksums and its attestation:

```sh
shasum -a 256 -c SHA256SUMS
gh attestation verify sandboxesd-darwin-arm64 --repo rheic/sandboxes-daemon
```

Release artifacts are the supported install path. A source build is described in [requirements](requirements.md) and is for development only.

## 2. Place the daemon next to `rsbx`

The installer puts `rsbx` in `~/.local/bin`. Put the daemon in the same directory so one `PATH` entry finds both binaries:

```sh
install -m 0755 sandboxesd-darwin-arm64 "$HOME/.local/bin/sandboxesd"
command -v rsbx sandboxesd
```

The daemon and CLI must come from compatible tagged releases. The published pair is CLI v0.0.54 with daemon v0.0.62 and API contract 0.0.27. Do not point the daemon at a socket or state directory owned by another installation.

## 3. Configure the runtime assets

The VM backend needs the pinned external components listed in `modules/sandboxes-runtime/build/manifest.yaml`:

- containerd and `ctr`;
- libkrun and the patched nerdbox shim, which must resolve before the stock shim on `PATH`;
- the matching guest kernel and EROFS root filesystem;
- `mkfs.erofs` and `mkfs.ext4`;
- the policy-enabled `gvproxy` build when guests need network access.

Build the exact pinned inputs with the runtime build instructions. Do not substitute an arbitrary system QEMU, shim, or gateway binary, and do not download unpinned dependencies.

## 4. Start the daemon with the VM backend

Point the daemon at the runtime assets you just built. The values below are placeholders for the paths your build produces; take the real ones from the pinned manifest:

```sh
sandboxesd \
  --state "$HOME/.sandboxes" \
  --socket "$HOME/.sandboxes/sandboxesd.sock" \
  --containerd "<containerd.sock from the runtime build>" \
  --runtime io.containerd.nerdbox.v1 \
  --snapshotter erofs \
  --image "<pinned guest image reference>" \
  --fifo-dir "<runtime FIFO directory>" \
  --gvproxy "<policy-enabled gvproxy binary>"
```

An empty `--containerd` keeps the daemon in state-only mode and never starts a VM. Networking stays disabled unless `--gvproxy` points at a compatible policy gateway. Leave the daemon running; the next steps use a second terminal.

`rsbx daemon start --detach` can start a daemon with the default settings, and `rsbx daemon status` reports the daemon it can identify. A daemon started with explicit VM runtime flags as above keeps its own process lifecycle; use `rsbx daemon status`, `rsbx daemon log-level`, and `rsbx daemon stop` to inspect or manage it. Stop signals only a daemon whose identity it can prove. If the daemon was started outside the CLI and its identity cannot be proven, stop refuses and explains how to stop it manually; on platforms that cannot discover the socket peer it decides from the control record. See [CLI reference](cli.md#daemon-lifecycle).

## 5. Run a microVM

Boot a guest shell in the current directory:

```sh
cd /path/to/project
rsbx run shell .
```

`run` creates or reuses the sandbox, starts it, and attaches the guest shell. The current directory is the default workspace, so only the project you chose is mounted. `--detach` returns after startup, and agent arguments follow `--`.

List what the daemon knows about:

```sh
rsbx ls
rsbx ls --json
```

Both commands use the default socket `$HOME/.sandboxes/sandboxesd.sock`. If you started the daemon elsewhere, pass `--socket PATH` or set `SANDBOXES_SOCKET`. Use `rsbx stop`, `rsbx start`, and `rsbx rm` for the rest of the lifecycle.

## State-only fallback (no VM)

State-only mode is a fallback for a machine that does not have the runtime assets yet, or for inspecting the local control plane without a guest. It never boots a VM:

```sh
sandboxesd \
  --state "$HOME/.sandboxes" \
  --socket "$HOME/.sandboxes/sandboxesd.sock"

rsbx ls
rsbx diagnose
```

These commands confirm that the CLI can reach the local daemon and inspect control-plane state. They do not boot a guest, prove VM isolation, or validate an agent session. VM-backed lifecycle and exec checks passed on macOS ARM64, but agent authentication and complete interactive workflows per agent remain unvalidated.

## Limits to keep in mind

- The validated native VM path targets macOS on Apple silicon only.
- Windows WHP is not implemented. Cloud commands (`move`, `ttl`, `volume`) are out of scope for the local alpha. Nested Docker workloads inside the guest remain blocked.
- No independent external security review has been completed; see the [security model](security.md).
- Docker built-in agents remain preview: image launch probes passed, but provider authentication and complete agent sessions did not. See [agents](agents.md).

## Where to go next

Read the [requirements](requirements.md) before building runtime components. See the [CLI reference](cli.md) for command syntax, [workspaces](workspaces.md), [networking](networking.md), and [credentials](credentials.md). The [Docker guide](docker.md) explains why account sign-in and guest Docker are separate. Read the [security model](security.md) before connecting a project or storing credentials.
