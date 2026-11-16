# Быстрый старт

Это руководство устанавливает выпущенную альфу Sandboxes от Rheic и загружает настоящую microVM на macOS ARM64. Основной путь — microVM: daemon управляет containerd, nerdbox shim и libkrun, а `rsbx run shell .` создаёт или переиспользует sandbox, запускает его и подключает shell гостя. Режим state-only — явно обозначенный резервный вариант для host-систем без runtime-артефактов; VM он не запускает.

Опубликованная альфа — это CLI `rsbx` v0.0.53, daemon `sandboxesd` v0.0.61 и локальный API-контракт 0.0.27. Бинарники публикуются как релизные артефакты с `SHA256SUMS` и SLSA-attestations. Live acceptance на macOS ARM64 покрыла create, start, exec, stop, start, delete, изоляцию между VM, opt-in матрицы IPv6 и QUIC и режим клона. Она не квалифицирует Windows, native Linux и rootless host-системы, а также облачные команды. Windows WHP не реализован, облачные команды вне области, независимый внешний security review не проводился.

## 1. Установите альфа-бинарники

Установщик скачивает CLI, проверяет контрольную сумму, подтверждает SLSA-аттестацию происхождения и ставит бинарник в `~/.local/bin`:

```sh
curl -fsSL https://raw.githubusercontent.com/rheic/sandboxes-cli/main/scripts/install.sh | sh
rsbx version    # rsbx version v0.0.53 для текущей альфы
```

Скачайте `sandboxesd` v0.0.61 для своей платформы из [релизов daemon](https://github.com/rheic/sandboxes-daemon/releases) и проверьте его по опубликованным контрольным суммам и аттестации:

```sh
shasum -a 256 -c SHA256SUMS
gh attestation verify sandboxesd-darwin-arm64 --repo rheic/sandboxes-daemon
```

Поддерживаемый путь установки — релизные артефакты. Сборка из исходников описана в разделе [системные требования](requirements.md) и нужна только для разработки.

## 2. Положите daemon рядом с `rsbx`

Установщик кладёт `rsbx` в `~/.local/bin`. Положите daemon в тот же каталог, чтобы одна запись `PATH` находила оба бинарника:

```sh
install -m 0755 sandboxesd-darwin-arm64 "$HOME/.local/bin/sandboxesd"
command -v rsbx sandboxesd
```

Daemon и CLI должны быть из совместимых tagged-релизов. Опубликованная пара — CLI v0.0.53 с daemon v0.0.61 и API-контрактом 0.0.27. Не направляйте daemon на сокет или каталог состояния другой установки.

## 3. Настройте runtime-артефакты

Для VM-backend нужны закреплённые внешние компоненты из `modules/sandboxes-runtime/build/manifest.yaml`:

- containerd и `ctr`;
- libkrun и patched nerdbox shim, который должен находиться в `PATH` раньше стандартного shim;
- совместимые guest kernel и корневую файловую систему EROFS;
- `mkfs.erofs` и `mkfs.ext4`;
- policy-enabled сборку `gvproxy`, если гостям нужен сетевой доступ.

Соберите точные закреплённые артефакты по инструкции сборки runtime. Не подменяйте их произвольными системными QEMU, shim или gateway-бинарниками и не загружайте незакреплённые зависимости.

## 4. Запустите daemon с VM-backend

Укажите daemon пути к собранным runtime-артефактам. Значения ниже — заглушки для путей, которые создаст ваша сборка; реальные берите из закреплённого манифеста:

```sh
sandboxesd \
  --state "$HOME/.sandboxes" \
  --socket "$HOME/.sandboxes/sandboxesd.sock" \
  --containerd "<containerd.sock из сборки runtime>" \
  --runtime io.containerd.nerdbox.v1 \
  --snapshotter erofs \
  --image "<закреплённая ссылка на guest image>" \
  --fifo-dir "<каталог FIFO runtime>" \
  --gvproxy "<policy-enabled бинарник gvproxy>"
```

Пустой `--containerd` оставляет daemon в режиме state-only, и VM не запускается. Сеть остаётся выключенной, пока `--gvproxy` не указывает на совместимый policy gateway. Оставьте daemon работать; следующие шаги выполняются во втором терминале.

`rsbx daemon start --detach` может запустить daemon с настройками по умолчанию, а `rsbx daemon status` показывает daemon, который удаётся идентифицировать. Daemon, запущенный с явными runtime-флагами VM, как выше, сохраняет собственный жизненный цикл процесса; используйте `rsbx daemon status`, `rsbx daemon log-level` и `rsbx daemon stop` для проверки и управления. Stop сигналит только тому daemon, чью идентичность удалось доказать. Если daemon запущен вне CLI и идентичность доказать нельзя, stop отказывается и объясняет, как остановить его вручную; на платформах без определения socket peer команда решает по control record. См. [справочник CLI](cli.md#daemon-lifecycle).

## 5. Запустите microVM

Загрузите shell гостя в текущем каталоге:

```sh
cd /путь/к/проекту
rsbx run shell .
```

`run` создаёт или переиспользует sandbox, запускает его и подключает shell гостя. Текущий каталог — workspace по умолчанию, поэтому монтируется только выбранный проект. `--detach` завершает команду после старта, а аргументы агента передаются после `--`.

Посмотрите, что известно daemon:

```sh
rsbx ls
rsbx ls --json
```

Обе команды используют сокет по умолчанию `$HOME/.sandboxes/sandboxesd.sock`. Если daemon запущен с другим путём, передайте `--socket PATH` или задайте `SANDBOXES_SOCKET`. Остальной lifecycle — это `rsbx stop`, `rsbx start` и `rsbx rm`.

## Резервный режим state-only (без VM)

Режим state-only — резервный вариант для машины, где runtime-артефакты ещё не подготовлены, или для проверки локальной control plane без гостя. VM он не запускает:

```sh
sandboxesd \
  --state "$HOME/.sandboxes" \
  --socket "$HOME/.sandboxes/sandboxesd.sock"

rsbx ls
rsbx diagnose
```

Эти команды проверяют, что CLI видит локальный daemon и состояние control plane. Они не загружают гостя, не подтверждают изоляцию VM и не проверяют сессию агента. VM-backed lifecycle и exec-проверки прошли на macOS ARM64, но авторизация агентов и полные интерактивные сценарии каждого агента пока не проверены.

## Что помнить об ограничениях

- Проверенный нативный VM-путь рассчитан только на macOS с Apple silicon.
- Windows WHP не реализован. Облачные команды (`move`, `ttl`, `volume`) вне области локальной альфы. Вложенные Docker workloads внутри гостя остаются заблокированными.
- Независимый внешний security review не проводился; см. [модель безопасности](security.md).
- Встроенные агенты Docker остаются preview: проверки запуска образов прошли, авторизация провайдера и полные сессии агентов — нет. См. [агенты](agents.md).

## Следующие шаги

Перед сборкой runtime прочитайте [системные требования](requirements.md). В [справочнике CLI](cli.md) описан интерфейс команд, отдельно доступны [workspace](workspaces.md), [сеть](networking.md) и [credentials](credentials.md). [Руководство Docker](docker.md) объясняет различие входа в аккаунт и Docker в guest. Перед подключением проекта или сохранением credentials изучите [модель безопасности](security.md).
