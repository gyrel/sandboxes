# Bundle для native runtime

Native runtime не публикуется отдельной загрузкой. Он закреплён внутри текущего alpha-bundle. Линия релиза — runtime v0.1.2 в `gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz`. Bundle содержит containerd с патчами, nerdbox shim, gvproxy, libkrun, libkrunfw, пропатченный ARM64 kernel Image и EROFS guest rootfs. Исходники bundle отмечены тегом в [runtime-репозитории](https://github.com/gyrel/sandboxes-runtime).

| Пункт | Значение |
|---|---|
| Линия runtime | v0.1.2 |
| Поставка | Закреплён внутри alpha-bundle r8 |
| Артефакт bundle | `gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz` |
| SHA-256 bundle | `e66b4d5fc1dab8e3bb193800a3c013057f789c454f321c55b36d528b23df8644` |

## Проверка bundle

Скачайте bundle и sidecar `.sha256` из [релизов проекта](https://github.com/gyrel/sandboxes/releases). Проверьте checksum архива **до извлечения**, затем извлеките его в пустой приватный каталог:

```sh
shasum -a 256 -c gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz.sha256
tar -xzf gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz -C /path/to/empty-private-dir
```

Managed launcher проверяет каждый runtime-артефакт внутри bundle по SHA-256 перед каждым запуском VM и отказывается запускать непроверенные байты. Собирать и проверять runtime вручную не нужно: launcher выполняет проверку каждого артефакта при старте.

## Что подтверждает проверка

Launcher подтверждает целостность артефактов и платформу, **но не** личность издателя или поведение runtime. Дайджесты опубликованных assets совпали с локально проверенными архивами. Linux и macOS запускали pinned Alpine ARM64 guest task; это покрывает basic boot и очистку task, но не полный Docker workload, egress или policy parity. macOS dylibs подписаны ad hoc и не notarized; её libkrun и graphics dependencies взяты из Homebrew bottles. См. [ограничения](limits.md).
