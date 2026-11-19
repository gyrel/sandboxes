# Native runtime bundles

Runtime code v0.0.40 uses the unchanged native assets published by [runtime v0.0.36](https://github.com/rheic/sandboxes-runtime/releases/tag/v0.0.36). That release publishes `rheic-runtime-v0.0.36-linux-arm64.tar.gz` and `rheic-runtime-v0.0.36-darwin-arm64.tar.gz`. Both contain containerd, ctr, patched nerdbox shim and gvproxy, libkrun, libkrunfw, patched ARM64 kernel Image, and EROFS guest rootfs. Every regular file is listed in `bundle.json` with size and SHA-256.

| Asset | SHA-256 |
|---|---|
| Linux ARM64 archive | `97391474f9d4bb4fee7281525baad0bb20803dc90166de6f747f5af5686ad982` |
| macOS ARM64 archive | `314968cd1ec1f5a85b4831f8ef99f42cc8c8c8380b6b7494418a552bebde17f7` |
| Patched kernel Image in both | `8a1b87b1b754be382aa9fea5159a9ec49a30c08a11afff6c88b42efcf7455081` |
| Guest rootfs in both | `d08f59e209e83436cf3e9e32aad6bc68bf815e99c86882e55cedd7336f416b35` |

Download both the archive for your platform and `SHA256SUMS` from the release. Verify the archive checksum **before extraction**, then extract into an empty private directory. From the matching runtime source tag, verify the exact inventory:

```sh
shasum -a 256 -c SHA256SUMS
tar -xzf rheic-runtime-v0.0.36-darwin-arm64.tar.gz -C /path/to/empty-private-dir
go run ./cmd/runtime-bundle verify --root /path/to/empty-private-dir --platform darwin/arm64
```

Use `linux/arm64` and the Linux archive on Linux. The check verifies content and platform, **not** publisher identity or runtime behavior. Published asset digests matched the locally verified archives. Linux and macOS each booted a pinned Alpine ARM64 guest task; this covers basic boot and task cleanup, not full Docker workload, egress or policy parity. macOS dylibs are ad hoc signed and not notarized; its libkrun and graphics dependencies came from Homebrew bottles. See [limits](limits.md).
