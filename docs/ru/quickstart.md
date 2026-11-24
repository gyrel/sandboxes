# Быстрый старт

Это руководство устанавливает опубликованную альфу Sandboxes от Rheic и запускает настоящую microVM на macOS ARM64. Основной путь — microVM: launcher поднимает закреплённый containerd, daemon управляет nerdbox shim и libkrun, а `rsbx run shell .` создаёт или переиспользует песочницу, запускает её и подключает гостевой шелл. State-only режим — помеченный fallback для хостов без runtime-ассетов; он не запускает VM.

Опубликованная альфа — это CLI `rsbx` v0.0.74, daemon `sandboxesd` v0.0.98 и локальный API-контракт 0.0.38, собранные в один проверенный alpha bundle с закрепленными runtime-ассетами и дайджестами. Бинарники поставляются с `SHA256SUMS`; launcher бандла проверяет каждый runtime-артефакт по SHA-256 перед каждым запуском VM и отказывается запускать непроверенные байты. Live acceptance на macOS ARM64 покрывает полный жизненный цикл VM, workspace, `cp`, публикацию портов, сохранение/загрузку шаблонов живым roundtrip-прогоном, хостовое хранилище секретов с custom-секретами и flow согласований, регистрацию MCP с challenge согласования, валидацию kit с daemon-политикой, skills, панели событий TUI и opt-in матрицы IPv6 и QUIC. Она не квалифицирует Windows, native Linux и rootless host-системы, а также облачные команды. Windows WHP не реализован, облачные команды вне области, независимый внешний security review не проводился.

## 1. Скачайте и проверьте alpha bundle

Бандл содержит CLI, daemon, закрепленный runtime (containerd с патчами, nerdbox shim, gvproxy, libkrun, ядро и гостевая rootfs), файл дайджестов и managed-лаунчер. Скачайте `rheic-sandboxes-alpha-darwin-arm64-r4.tar.gz` и его `.sha256` из [релизов проекта](https://github.com/rheic/sandboxes/releases), затем:

```sh
shasum -a 256 -c rheic-sandboxes-alpha-darwin-arm64-r4.tar.gz.sha256
tar -xzf rheic-sandboxes-alpha-darwin-arm64-r4.tar.gz
cd rheic-sandboxes-alpha-darwin-arm64
shasum -a 256 -c SHA256SUMS
```

Хосту нужен Homebrew `e2fsprogs` (`brew install e2fsprogs`) для `mkfs.ext4`; лаунчер находит его сам и быстро падает с этой подсказкой, если он отсутствует.

## 2. Установите CLI и запустите managed daemon

```sh
mkdir -p ~/.local/bin
install -m 0755 bin/rsbx ~/.local/bin/rsbx
bin/rheicd-launch.sh &
~/.local/bin/rsbx daemon status   # running, с версиями и API-контрактом
```

Лаунчер сам запускает containerd, указывает daemon на bundled runtime и включает проверку артефактов по дайджестам перед каждым запуском VM (`--artifact-digests` плюс закрепленный набор `--runtime-artifact`). Никогда не смешивайте бинарники из разных релизов: опубликованный набор — CLI v0.0.74, daemon v0.0.98, API-контракт 0.0.38. Не направляйте daemon на сокет или каталог состояния другой установки.

Для разработки против уже существующего локального runtime можно запустить `bin/sandboxesd` с явными флагами (`--ctr`, `--gvproxy`, `--proxy-helper`); state-only режим описан ниже. Escape hatch `--allow-unmanaged-runtime` существует, но не является поддерживаемым путем альфы: используйте лаунчер, чтобы дайджесты оставались включеными.

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

Обе команды используют сокет по умолчанию `$HOME/.sandboxes/sandboxesd.sock` (лаунчер учитывает `RHEIC_STATE_DIR`). Если daemon запущен в другом месте, передайте `--socket PATH` или задайте `SANDBOXES_SOCKET`. Остальное — `rsbx stop`, `rsbx rm`, `rsbx prune`; остановленная песочница стартует автоматически при `exec`.

## 4. Попробуйте основные поверхности

```sh
rsbx ports NAME                          # опубликованные порты
rsbx cp ./file.txt NAME:/tmp/file.txt    # файлы в обе стороны
rsbx template save NAME mytpl && rsbx template ls
rsbx secret ls && rsbx secret set-custom --host api.example.com --env API_KEY
rsbx policy check network api.openai.com --method GET   # проверка одного запроса по сохранённым правилам
rsbx kit validate ./my-kit --offline
rsbx mcp add docs --url https://mcp.example.com/mcp   # challenge согласования регистрации
rsbx policy approval ls                  # ожидающие consent-запросы
rsbx tui                                 # панель с живыми событиями
```

Больше сквозных сценариев с точным ожидаемым выводом — в [пользовательских кейсах](user-cases.md).

## State-only fallback (без VM)

State-only режим — fallback для машины без runtime-ассетов или для осмотра локальной контрольной плоскости без гостя. Он не запускает VM:

```sh
sandboxesd --state "$HOME/.sandboxes-rheic-check" --socket "$HOME/.sandboxes-rheic-check/sandboxesd.sock"

rsbx --socket "$HOME/.sandboxes-rheic-check/sandboxesd.sock" ls
rsbx --socket "$HOME/.sandboxes-rheic-check/sandboxesd.sock" diagnose
```

Эти команды подтверждают, что CLI видит локальный daemon и состояние контрольной плоскости. Они не запускают гостя, не доказывают изоляцию VM и не валидируют сессию агента.

## Помните про ограничения

- Валидированный native VM путь — только macOS на Apple silicon.
- Windows WHP не реализован. Облачные команды (`move`, `ttl`, `volume`) вне области локальной альфы. Вложенные Docker-нагрузки в госте остаются заблокированными.
- Регистрация MCP-серверов требует host-согласия; доверенный OS-backed approval и интерактивный OAuth для удалённых MCP-серверов ещё не выпущены, поэтому approve-пути fail-closed. Custom-секреты `--ref`/`--command` и L7 HTTPS interception ждут те же seams.
- Независимый внешний security review не проводился; см. [модель безопасности](security.md).
- Встроенные Docker-агенты остаются preview: image launch probes прошли, но провайдерская аутентификация и полные сессии агентов — нет. См. [агенты](agents.md).

## Что дальше

Прочитайте [требования](requirements.md) перед сборкой runtime-компонентов. Смотрите [пользовательские кейсы](user-cases.md) для проверенных сценариев, [справочник CLI](cli.md) для синтаксиса команд, [workspace](workspaces.md), [сеть](networking.md) и [credentials](credentials.md). [Руководство Docker](docker.md) объясняет, почему вход в аккаунт Docker и гостевой Docker — разные вещи. Прочитайте [модель безопасности](security.md), прежде чем подключать проект или хранить credentials.
