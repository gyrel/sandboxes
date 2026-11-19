# Get started

This guide verifies the **released local control plane** on macOS ARM64. A VM also needs configured native runtime processes and assets; the CLI installer alone does not start one.

## Install the released CLI and daemon

Install `rsbx` v0.0.63 with the [CLI installer](https://github.com/rheic/sandboxes-cli/blob/main/scripts/install.sh), or download its platform asset from the [CLI release](https://github.com/rheic/sandboxes-cli/releases/tag/v0.0.63). Check `SHA256SUMS` and the CLI attestation before installation. Download `sandboxesd` v0.0.72 from the [daemon release](https://github.com/rheic/sandboxes-daemon/releases/tag/v0.0.72) and verify its checksum and attestation as well. Keep both binaries in your own `PATH`; do not replace Docker's `sbx`.

```sh
rsbx version
sandboxesd --version
```

## Inspect the local control plane

Use a new private state directory and socket. Starting without `--containerd` is **state-only**: the daemon can answer CLI requests but cannot boot a guest.

```sh
mkdir -p "$HOME/.sandboxes"
sandboxesd --state "$HOME/.sandboxes" --socket "$HOME/.sandboxes/sandboxesd.sock"
```

In another terminal:

```sh
rsbx ls --json
rsbx diagnose
```

Stop the process you started when finished. The commands above should not create a sandbox. `rsbx daemon stop` only signals a daemon whose identity it can prove; an externally started process may need to be stopped from its original terminal.

## Boot a VM

The VM path requires a compatible containerd instance, patched nerdbox shim, libkrun, kernel, EROFS rootfs, `gvproxy` for networking, and filesystem tools. [Runtime v0.0.36](runtime.md) publishes these native assets for ARM64, with exact inventories; runtime code v0.0.39 uses the same native assets. The released CLI v0.0.63 / daemon v0.0.72 pair and those assets were qualified for read-only shared skills on macOS ARM64 and Linux/KVM ARM64. **Other workloads and full Docker parity are not qualified.** Follow the runtime build and daemon configuration for an isolated VM test; do not treat the state-only check as VM evidence.

Once the VM backend is configured, `rsbx run shell .` creates or reuses, starts, and attaches to a local guest. The current directory is mounted by default; choose a private project or use `--clone` when you want a guest copy. See [CLI](cli.md) and [limits](limits.md).
