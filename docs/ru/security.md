# Модель безопасности

Rheic создаётся для запуска задач агента в изолированных microVM-песочницах и хранения host credentials под контролем host-системы. Это направление реализации, а не общее заключение о безопасности. Rheic пока находится в стадии pre-alpha.

## Границы доверия

- Локальный CLI подключается к daemon через сокет с ограниченными правами.
- Daemon управляет метаданными песочниц и runtime.
- VM-runtime отделяет guest-нагрузки от host-процессов.
- При включённом policy gateway сетевой доступ запрещён по умолчанию.
- Provider credentials хранятся в системном хранилище host. Они не должны попадать в метаданные песочниц, SQLite или логи.

## Практика безопасной работы

- Проверяйте workspace перед передачей агенту с правом записи. Для входных данных используйте `:ro`.
- Оставляйте сеть закрытой, пока задача не потребует доступа. Разрешайте только нужные адреса и порты.
- Не помещайте credentials в аргументы команд или обычные переменные среды. Используйте поддерживаемые команды host credential vault.
- Host hooks, MCP stdio servers, lifecycle-команды и writable mounts выполняются с правами соответствующего host-процесса. Используйте их только с явным одобрением и ограниченным окружением.
- Для экспериментов создавайте отдельные временные каталоги и уникальные имена песочниц. Удаляйте только ресурсы, созданные вашим запуском.

## Текущие ограничения

Rheic пока не заявляет полную совместимость с Docker Sandboxes или завершённую production-границу безопасности. Ограниченный VM-backed lifecycle прошёл acceptance на macOS ARM64. Linux ARM64 guest-task также пережила detach/reattach managed containerd в Ubuntu Lima/QEMU с nested KVM на macOS; native Linux host и rootless-режим не квалифицированы. Опциональный профиль `--docker` запускает Docker daemon внутри guest, но вложенные операции `docker run`, `docker load`, `docker build` и Compose пока блокируются ограничениями `unshare` в текущем runtime. Это ограничение не означает, что сама VM не запускается. Host Docker socket не монтируется. Поддержка платформ неполная; Windows WHP не проверялся на физическом Windows-оборудовании. Не закрыты жизненный цикл OAuth-токенов, очистка после сбоя host/питания, независимый security review и полная проверка сетевых обходов. Некоторые сценарии registry и агентов не завершены или fail-closed. Service-secret proxy ограничен одним настроенным service на sandbox; остаются fault matrix и независимый security review.

Черновой runtime PR [#40](https://github.com/rheic/sandboxes-runtime/pull/40) меняет очистку Linux bundle в закреплённом containerd v2.4.2: перед изменением он без побочных эффектов проверяет host-side rootfs и ожидаемый work path, затем fail closed отказывает при mount или неожиданном пути. Он сверяет symlink bundle/work с настроенным work root, сохраняет work data при неудачной очистке bundle и применяет confined remover при startup cleanup, откате неудачного создания и замене оставшегося work path. В recovery удалён прямой вызов рекурсивного unmount rootfs. Bundle boundary controls прошли дважды, гонка same-UID mount после rename — 10/10. Mount-контроли orphan work recovery и stale work replacement прошли по два раза: tmpfs и marker сохранялись, после тестовой размонтировки позитивная очистка завершалась. Проверки выполнены в Ubuntu 24.04 ARM64 Lima/QEMU VM на macOS с nested KVM, а не на native Linux host. Все 12 hosted CI checks прошли для текущего кандидата. Кандидат не подписан, managed daemon пока его не использует и не проверяет, поэтому поведение опубликованной версии очистки не квалифицировано. Managed launcher fail-closed завершается без `CAP_SYS_ADMIN`; это подтверждает отказ в rootless-режиме, но не поддержку rootless workload.

Runtime и daemon содержат exec/PTY пути; ограниченный VM-backed lifecycle прошёл live acceptance на macOS ARM64. Это не подтверждает полные agent-сценарии или другие платформы. Проверенные границы и ограничения компонентов описаны в разделах [требования](requirements.md), [архитектура](architecture.md), [workspace](workspaces.md), [сеть](networking.md) и [credentials](credentials.md).

В [руководстве Docker](docker.md) объяснена разница между входом в Docker account на host, доступом к registry и Docker Engine внутри песочницы.

На этой странице описаны модель безопасности и известные ограничения. Отсутствие результата проверки означает unknown или unverified, а не безопасность по умолчанию.
