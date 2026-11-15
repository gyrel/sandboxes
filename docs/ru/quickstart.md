# Быстрый старт

Это руководство устанавливает выпущенную альфу Sandboxes от Rheic и загружает настоящую microVM на macOS ARM64. Основной путь — microVM: daemon управляет containerd, nerdbox shim и libkrun, а `rsbx run shell .` создаёт или переиспользует sandbox, запускает его и подключает shell гостя. Режим state-only — явно обозначенный резервный вариант для host-систем без runtime-артефактов; VM он не запускает.

Текущая альфа — это CLI `rsbx` v0.0.49 и daemon `sandboxesd` v0.0.56. Оба публикуются как релизные артефакты с `SHA256SUMS` и SLSA-attestations. Live acceptance на macOS ARM64 покрыла create, start, exec, stop, start, delete, изоляцию между VM, opt-in матрицы IPv6 и QUIC, registry broker и режим клона. Она не квалифицирует Windows, native Linux и rootless host-системы, облачные команды и вложенные Docker workloads, а также не заменяет независимый внешний security review.

## 1. Установите альфа-бинарники

Установщик скачивает CLI, проверяет контрольную сумму, подтверждает SLSA-аттестацию происхождения и ставит бинарник в `~/.local/bin`:

```sh
curl -fsSL https://raw.githubusercontent.com/rheic/sandboxes-cli/main/scripts/install.sh | sh
rsbx version    # rsbx version v0.0.49 для текущей альфы
```

Скачайте `sandboxesd` v0.0.56 для своей платформы из [релизов daemon](https://github.com/rheic/sandboxes-daemon/releases) и проверьте его по опубликованным контрольным суммам и аттестации:

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

Daemon и CLI должны быть из совместимых tagged-релизов. Не направляйте daemon на сокет или каталог состояния другой установки.

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

## 5. Запустите microVM

Загрузите shell гостя в текущем каталоге:

```sh
cd /path/to/project
rsbx run shell .
```

`run` создаёт или переиспользует sandbox, запускает его и подключает shell гостя. Текущий каталог — workspace по умолчанию, поэтому монтируется только выбранный проект. `--detach` завершает команду после старта, а аргументы агента передаются после `--`.

Посмотрите, что известно daemon:

```sh
rsbx ls
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

Эти команды проверяют, что CLI видит локальный daemon и состояние control plane. Они не загружают гостя, не подтверждают изоляцию VM и не проверяют сессию агента. Runtime и daemon содержат exec/PTY пути, а live acceptance прошла на macOS ARM64, но авторизация агентов и полные интерактивные сценарии каждого агента пока не проверены.

## Что помнить об ограничениях

- Проверенный нативный VM-путь рассчитан только на macOS с Apple silicon.
- Windows WHP, облачные команды (`move`, `ttl`, `volume`) и вложенные Docker workloads внутри гостя не поддерживаются.
- Независимый внешний security review ещё не проводился; см. [модель безопасности](security.md).
- Встроенные агенты Docker остаются preview: проверки запуска образов прошли, авторизация провайдера и полные сессии агентов — нет. См. [агенты](agents.md).

## Следующие шаги

Перед сборкой runtime прочитайте [системные требования](requirements.md). В [справочнике CLI](cli.md) описан интерфейс команд, отдельно доступны [workspace](workspaces.md), [сеть](networking.md) и [credentials](credentials.md). [Руководство Docker](docker.md) объясняет различие входа в аккаунт и Docker в guest. Перед подключением проекта или сохранением credentials изучите [модель безопасности](security.md).
