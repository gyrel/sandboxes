# Native runtime bundles

Код runtime v0.0.41 использует неизменные native assets из [runtime v0.0.36](https://github.com/gyrel/sandboxes-runtime/releases/tag/v0.0.36). Тот релиз содержит `rheic-runtime-v0.0.36-linux-arm64.tar.gz` и `rheic-runtime-v0.0.36-darwin-arm64.tar.gz`. В каждом есть containerd, ctr, patched nerdbox shim и gvproxy, libkrun, libkrunfw, patched ARM64 kernel Image и EROFS guest rootfs. Каждый обычный файл указан в `bundle.json` с размером и SHA-256.

| Asset | SHA-256 |
|---|---|
| Linux ARM64 archive | `97391474f9d4bb4fee7281525baad0bb20803dc90166de6f747f5af5686ad982` |
| macOS ARM64 archive | `314968cd1ec1f5a85b4831f8ef99f42cc8c8c8380b6b7494418a552bebde17f7` |
| Patched kernel Image в обоих | `8a1b87b1b754be382aa9fea5159a9ec49a30c08a11afff6c88b42efcf7455081` |
| Guest rootfs в обоих | `d08f59e209e83436cf3e9e32aad6bc68bf815e99c86882e55cedd7336f416b35` |

Скачайте архив своей платформы и `SHA256SUMS`. Проверьте checksum архива **до извлечения**, затем извлеките в пустой приватный каталог. Из исходников того же runtime-тега проверьте точный inventory:

```sh
shasum -a 256 -c SHA256SUMS
tar -xzf rheic-runtime-v0.0.36-darwin-arm64.tar.gz -C /path/to/empty-private-dir
go run ./cmd/runtime-bundle verify --root /path/to/empty-private-dir --platform darwin/arm64
```

На Linux используйте Linux-архив и `linux/arm64`. Проверка подтверждает content и платформу, **но не** личность издателя или runtime behavior. GitHub asset digests совпали с локально проверенными архивами. Linux и macOS запускали pinned Alpine ARM64 guest task; это basic boot и cleanup, а не полный Docker workload, egress или policy parity. macOS dylibs подписаны ad hoc и не notarized; её libkrun и graphics dependencies взяты из Homebrew bottles. См. [ограничения](limits.md).
