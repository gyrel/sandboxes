# Архитектура

Gyrel — локальная control plane для агентских sandbox-сессий. У компонентов разные обязанности; собирать их нужно из совместимых версий модулей.

```text
rsbx CLI / terminal dashboard
          │ local API through sandboxes-go-sdk
          ▼
      sandboxesd ───── host credential vault
          │
          ├── runtime adapter ── microVM ── guest agent
          └── network gateway ─── guest network policy
```

## Control plane

CLI вызывает локальный daemon через официальный Go SDK и публичный API-модуль. Daemon владеет метаданными sandbox и координирует runtime, workspace, политику и операции credentials. В state-only режиме он может управлять метаданными, но не запускает VM. Для выполнения кода guest нужен настроенный runtime backend.

## Runtime и guest

VM runtime, guest image, shim и вспомогательные бинарники — внешние зависимости с привязкой к версиям. Ограниченный VM-backed lifecycle проверен на macOS с Apple silicon. Отдельная Linux ARM64 guest-task прошла detach/reattach managed containerd в Ubuntu Lima/QEMU с nested KVM на macOS. Это не квалифицирует native Linux host или rootless-режим; Windows WHP не реализован. Агент запускается в guest; mounts workspace определяют доступ к данным проекта на хосте.

## Сетевой периметр

Отдельный gateway при наличии конфигурации применяет поддерживаемую политику исходящего трафика guest. Новые sandboxes по умолчанию используют профиль egress `allow-all`, как и Docker `sbx`; явные deny-правила и приоритет org deny продолжают действовать, а `deny-all` остаётся доступным. Отсутствие gateway не означает свободный доступ: сетевые функции могут быть недоступны. Принятый CLI синтаксис правила не доказывает, что конкретная сборка gateway его обеспечивает. См. [Сеть и порты](networking.md).

## Credentials

Secrets хранятся в системном хранилище credentials хоста. Daemon раскрывает только поддерживаемые и явно запрошенные сценарии; сохранённые credentials автоматически не передаются в guest. Авторизация аккаунта Docker не равна доступу к Docker Engine из guest. См. [Credentials](credentials.md) и [Docker](docker.md).

## Статус проверки

Gyrel — альфа-ПО. Успешный ответ CLI или state-only daemon не подтверждает изоляцию VM. Windows WHP не реализован, облачные команды вне области, а независимый security review, подпись и проверка upgrade/rollback остаются открытыми блокерами. Текущие ограничения перечислены в разделе [Безопасность](security.md).
