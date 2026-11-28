# Native runtime bundles

The native runtime is not published as a separate download. It is pinned inside the current
alpha bundle. The release line is runtime v0.1.2, shipped in `gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz`.
The bundle contains containerd with patches, the nerdbox shim, gvproxy, libkrun, libkrunfw, a
patched ARM64 kernel Image, and the EROFS guest rootfs. The bundle source is tagged in the
[runtime repository](https://github.com/gyrel/sandboxes-runtime).

| Item | Value |
|---|---|
| Runtime line | v0.1.2 |
| Distribution | Pinned inside the alpha r8 bundle |
| Bundle artifact | `gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz` |
| Bundle SHA-256 | `e66b4d5fc1dab8e3bb193800a3c013057f789c454f321c55b36d528b23df8644` |

## Verify the bundle

Download the bundle and its `.sha256` sidecar from the [project releases](https://github.com/gyrel/sandboxes/releases).
Verify the archive checksum **before extraction**, then extract into an empty private directory:

```sh
shasum -a 256 -c gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz.sha256
tar -xzf gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz -C /path/to/empty-private-dir
```

The managed launcher verifies every runtime artifact inside the bundle by SHA-256 before each
VM launch and refuses to run unverified bytes. You do not assemble or verify the runtime by
hand; the launcher performs the per-artifact check at start.

## What the check proves

The launcher confirms artifact integrity and platform, **not** publisher identity or runtime
behavior. Published asset digests matched the locally verified archives. Linux and macOS each
booted a pinned Alpine ARM64 guest task; this covers basic boot and task cleanup, not full
Docker workload, egress or policy parity. macOS dylibs are ad hoc signed and not notarized;
its libkrun and graphics dependencies came from Homebrew bottles. See [limits](limits.md).
