# Системные требования

Gyrel — альфа-ПО с опубликованными релизными артефактами. Проверенный нативный VM-путь рассчитан на macOS с Apple silicon. Перед запуском VM соберите модули и подготовьте runtime-артефакты.

Текущая релизная линия — CLI `rsbx` v0.0.79, daemon `sandboxesd` v0.0.103 и локальный API-контракт 0.0.39, SDK 0.0.36 и runtime v0.1.2. Текущий alpha bundle — `alpha-2026-11-26` (`gyrel-sandboxes-alpha-darwin-arm64-r5final.tar.gz`). Более ранний bundle, опубликованный под прежним брендом, содержит CLI v0.0.74, daemon v0.0.98 и API-контракт 0.0.38. Устанавливайте релизные бинарники из релизов проекта; сборка из исходников нужна только для разработки.

## Поддерживаемая среда разработки

| Host-система | Текущий статус |
|---|---|
| macOS с Apple silicon | Нативный VM-путь проверялся локально; квалификация релиза не завершена |
| Linux host с KVM | Linux ARM64 guest-task прошёл проверку detach/reattach в Lima/QEMU с nested KVM на macOS; native Linux host и rootless-квалификация остаются открытыми |
| Windows с WHP | Не реализовано; для общего использования недоступно |

Актуальные результаты и блокеры платформ смотрите в плане проекта.

## Инструменты сборки

Для сборки из исходников нужны Go 1.27 и tagged-репозитории модулей Gyrel. Каждый модуль — отдельный Go-модуль; `modules/go.work` предназначен для локальной разработки. Релизные сборки используют tagged-версии без подмены workspace.

Соберите CLI и daemon из каталогов модулей:

```sh
cd modules/sandboxes-cli
mkdir -p ./bin
go build -o ./bin/rsbx ./cmd/rsbx

cd ../sandboxes-daemon
mkdir -p ./bin
go build -o ./bin/sandboxesd ./cmd/sandboxesd
```

Эти команды только собирают бинарники. Они не устанавливают системную службу, не настраивают keychain и не готовят VM-runtime.

## Компоненты VM-runtime

Для нативного VM-backend нужны закреплённые компоненты из `modules/sandboxes-runtime/build/manifest.yaml`:

- containerd и `ctr`
- libkrun и nerdbox shim
- соответствующие guest kernel и EROFS root filesystem
- policy-enabled сборка `gvproxy`, если нужен сетевой доступ
- `mkfs.erofs` и `mkfs.ext4` для образов и хранилища runtime

Процесс containerd должен находить patched nerdbox shim раньше штатного shim через `PATH`. Собирайте точные версии по инструкции runtime. Не подменяйте их произвольными системными бинарниками QEMU, shim или gateway.

## Настройка runtime

Если `--containerd` не задан, daemon работает в state-only режиме. Этот режим не запускает VM. VM-конфигурации нужны явные пути к сокету containerd, совместимому runtime, образу и guest-артефактам. Сеть отключена, пока daemon не настроен с совместимым policy gateway.

В [быстром старте](quickstart.md) объяснена разница между state-only и VM-режимами. В [архитектуре](architecture.md) описаны границы компонентов.
