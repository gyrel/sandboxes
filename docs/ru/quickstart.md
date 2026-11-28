# Быстрый старт

Это руководство устанавливает опубликованную альфу Sandboxes от Gyrel и запускает microVM на macOS ARM64. Основной путь — microVM. Launcher поднимает закреплённый containerd, а daemon управляет nerdbox shim и libkrun. Команда `rsbx run shell .` создаёт или переиспользует песочницу, запускает её и подключает гостевой шелл. State-only режим — помеченный fallback для хостов без runtime-ассетов; он не запускает VM.

Опубликованная альфа — это CLI `rsbx` v0.0.85, daemon `sandboxesd` v0.0.108 и локальный API-контракт 0.0.38, собранные в один проверенный alpha bundle с закрепленными runtime-ассетами и дайджестами. Бинарники поставляются с `SHA256SUMS`; launcher бандла проверяет каждый runtime-артефакт по SHA-256 перед каждым запуском VM и отказывается запускать непроверенные байты. Live acceptance на macOS ARM64 покрывает полный жизненный цикл VM, workspace, `cp`, публикацию портов, сохранение/загрузку шаблонов живым roundtrip-прогоном, хостовое хранилище секретов с custom-секретами и flow согласований, регистрацию MCP с challenge согласования, валидацию kit с daemon-политикой, skills, панели событий TUI, opt-in матрицы IPv6 и QUIC, аудит egress с корреляционными штампами (allow пишется до соединения, deny-by-rule исполняется) и fail-closed diagnose-бандл (отказ доказан planted PEM-ключом: архив не создан, в stderr только имена правил). Гостевой DNS через bundled gvproxy пока не резолвится (открытый срез); переключение deny при переполнении audit-стока доказано юнит-тестами, живая проверка запланирована на Linux. Она не квалифицирует Windows, native Linux и rootless host-системы, а также облачные команды. Windows WHP не реализован, облачные команды вне области, независимый внешний security review не проводился.

## 1. Скачайте и проверьте alpha bundle

Бандл содержит CLI, daemon, закрепленный runtime (containerd с патчами, nerdbox shim, gvproxy, libkrun, ядро и гостевая rootfs), файл дайджестов и managed-лаунчер. Скачайте `gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz` и его `.sha256` из [релизов проекта](https://github.com/gyrel/sandboxes/releases). Релиз опубликован как `alpha-2026-11-28-r8`. Затем выполните:

```sh
shasum -a 256 -c gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz.sha256
tar -xzf gyrel-sandboxes-alpha-darwin-arm64-r8.tar.gz
cd gyrel-sandboxes-alpha-darwin-arm64
shasum -a 256 -c SHA256SUMS
```

Хосту нужен Homebrew `e2fsprogs` (`brew install e2fsprogs`) для `mkfs.ext4`; лаунчер находит его сам и быстро падает с этой подсказкой, если он отсутствует.

## 2. Установите CLI и запустите managed daemon

```sh
mkdir -p ~/.local/bin
install -m 0755 bin/rsbx ~/.local/bin/rsbx
bin/gyreld-launch.sh &
~/.local/bin/rsbx daemon status   # running, with version and API contract
```

Лаунчер сам запускает containerd, указывает daemon на bundled runtime и включает проверку артефактов по дайджестам перед каждым запуском VM (`--artifact-digests` плюс закрепленный набор `--runtime-artifact`). Никогда не смешивайте бинарники из разных релизов. Опубликованный набор — CLI v0.0.85, daemon v0.0.108, API-контракт 0.0.38. Не направляйте daemon на сокет или каталог состояния другой установки. В бандле лаунчер называется `bin/gyreld-launch.sh`. В старых архивах (r4 и раньше, опубликованных под прежним брендом) находится `bin/rheicd-launch.sh`; запускайте то имя, которое лежит в распакованном каталоге `bin/`.

Для разработки против уже существующего локального runtime можно запустить `bin/sandboxesd` с явными флагами (`--ctr`, `--gvproxy`, `--proxy-helper`); state-only режим описан ниже. Escape hatch `--allow-unmanaged-runtime` существует, но не поддерживается в альфе: используйте лаунчер, чтобы дайджесты оставались включёнными.

## 3. Запустите microVM

```sh
cd /path/to/project
rsbx run shell .
```

`run` создаёт или переиспользует песочницу, запускает её и подключает гостевой шелл. Текущий каталог — workspace по умолчанию; в госте он монтируется по тому же абсолютному пути. `--detach` возвращает управление после старта, аргументы агента идут после `--`.

```sh
rsbx ls
rsbx ls --json
```

Обе команды используют сокет по умолчанию `$HOME/.sandboxes/sandboxesd.sock`. Лаунчер учитывает `GYREL_STATE_DIR`. Устаревшая `RHEIC_STATE_DIR` по-прежнему учитывается, но логирует предупреждение deprecation; переименуйте её в `GYREL_STATE_DIR`. Если daemon запущен в другом месте, передайте `--socket PATH` или задайте `SANDBOXES_SOCKET`. Остальное — `rsbx stop`, `rsbx rm`, `rsbx prune`; остановленная песочница стартует автоматически при `exec`. `rsbx run` и `rsbx create` принимают `--label KEY=VALUE`, а `rsbx prune --filter label=KEY=VALUE` выбирает песочницы по метке.

## 4. Попробуйте основные поверхности

```sh
rsbx ports NAME                          # published ports
rsbx cp ./file.txt NAME:/tmp/file.txt    # files both ways
rsbx template save NAME mytpl && rsbx template ls
rsbx secret ls && rsbx secret set-custom --host api.example.com --env API_KEY
rsbx policy check network api.openai.com --method GET   # evaluate one request against stored rules
rsbx kit validate ./my-kit --offline
rsbx mcp add docs --url https://mcp.example.com/mcp   # registration approval challenge
rsbx policy approval ls                  # pending consent requests
rsbx tui                                 # dashboard with live events
```

`rsbx` публикует host-порты только на loopback. Внешние host bindings требуют allowlist в настройках daemon `network.publish.allowedCIDRs` и недоступны через CLI в этой сборке. Копирование с хоста печатает примечание с именами скопированных файлов (basenames), а `cp` из хоста в гостя не поддерживается на Windows в этой сборке.

Больше сквозных сценариев с точным ожидаемым выводом — в [пользовательских кейсах](user-cases.md).

## State-only fallback (без VM)

State-only режим — fallback для машины без runtime-ассетов или для осмотра локальной контрольной плоскости без гостя. Он не запускает VM:

```sh
sandboxesd --state "$HOME/.sandboxes-gyrel-check" --socket "$HOME/.sandboxes-gyrel-check/sandboxesd.sock"

rsbx --socket "$HOME/.sandboxes-gyrel-check/sandboxesd.sock" ls
rsbx --socket "$HOME/.sandboxes-gyrel-check/sandboxesd.sock" diagnose
```

Эти команды подтверждают, что CLI видит локальный daemon и состояние контрольной плоскости. Они не запускают гостя, не доказывают изоляцию VM и не валидируют сессию агента.

## Помните про ограничения

- Валидированный native VM путь — только macOS на Apple silicon.
- Windows WHP не реализован. Облачные команды (`move`, `ttl`, `volume`) вне области локальной альфы. Вложенные Docker-нагрузки в госте остаются заблокированными.
- Регистрация MCP-серверов требует host-согласия. Доверенный OS-backed approval и интерактивный OAuth для удалённых MCP-серверов ещё не выпущены, поэтому approve-пути fail-closed. Custom-секреты `--ref`/`--command` и L7 HTTPS interception ждут закрытия тех же пробелов.
- Независимый внешний security review не проводился; см. [модель безопасности](security.md).
- Встроенные Docker-агенты остаются preview: image launch probes прошли, но провайдерская аутентификация и полные сессии агентов — нет. См. [агенты](agents.md).

## Что дальше

Прочитайте [требования](requirements.md) перед сборкой runtime-компонентов. Смотрите [пользовательские кейсы](user-cases.md) для проверенных сценариев, [справочник CLI](cli.md) для синтаксиса команд, [workspace](workspaces.md), [сеть](networking.md) и [credentials](credentials.md). [Руководство Docker](docker.md) объясняет, почему вход в аккаунт Docker и гостевой Docker — разные вещи. Прочитайте [модель безопасности](security.md), прежде чем подключать проект или хранить credentials.
