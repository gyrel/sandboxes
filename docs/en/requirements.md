# System requirements

Gyrel is alpha software with published release artifacts. The validated native VM path currently targets macOS on Apple silicon. Build and configure the runtime artifacts before trying the VM workflow.

The current release line is CLI `rsbx` v0.0.80, daemon `sandboxesd` v0.0.104, and local API contract 0.0.38, with SDK 0.0.36 and runtime v0.1.2. The current alpha bundle is `alpha-2026-11-26-r6` (`gyrel-sandboxes-alpha-darwin-arm64-r6.tar.gz`). The earlier bundle, published under the previous brand, ships CLI v0.0.74, daemon v0.0.98, and API contract 0.0.38. Install released binaries from the project releases; build from source only for development.

## Supported development host

| Host | Current status |
|---|---|
| macOS on Apple silicon | Native VM path has local validation; release qualification remains open |
| Linux host with KVM | A Linux ARM64 guest task passed a managed-service detach/reattach test in Lima/QEMU with nested KVM on macOS; native Linux host and rootless qualification remain open |
| Windows with WHP | Not implemented; not available for general use |

Use the project plan for current validation evidence and platform blockers.

## Build tools

A source build uses Go 1.27 and the tagged Gyrel module repositories. The modules are separate Go modules; `modules/go.work` is for local development. Release builds must use tagged versions without workspace substitutions.

Build the CLI and daemon from their module directories:

```sh
cd modules/sandboxes-cli
mkdir -p ./bin
go build -o ./bin/rsbx ./cmd/rsbx

cd ../sandboxes-daemon
mkdir -p ./bin
go build -o ./bin/sandboxesd ./cmd/sandboxesd
```

These commands build binaries only. They do not install a system service, configure a keychain, or prepare a VM runtime.

## VM runtime components

The native VM backend also needs the pinned components in `modules/sandboxes-runtime/build/manifest.yaml`:

- containerd and `ctr`
- libkrun and the nerdbox shim
- the matching guest kernel and EROFS root filesystem
- the policy-enabled `gvproxy` build when network access is required
- `mkfs.erofs` and `mkfs.ext4` for runtime image and storage tasks

The containerd process must find the patched nerdbox shim before the stock shim on `PATH`. Use the runtime build instructions to build the exact pinned inputs. Do not substitute an arbitrary system QEMU, shim, or gateway binary.

## Runtime configuration

The daemon starts in state-only mode when `--containerd` is empty. State-only mode does not start VMs. A VM configuration requires the explicit containerd socket, a compatible runtime, image, and the guest artifacts. Networking stays disabled unless the daemon receives a compatible policy gateway.

See the [quick start](quickstart.md) for the distinction between state-only mode and the VM backend, and the [architecture guide](architecture.md) for component boundaries.
