# Справочник CLI

Каноничный пользовательский бинарник — `rsbx`. Текущая релизная линия — CLI `rsbx` v0.0.76 с daemon `sandboxesd` v0.0.101, локальным API-контрактом 0.0.39, SDK 0.0.36 и runtime v0.1.0 — первыми тегами Gyrel. Большинство команд принимают `--socket PATH`; переменная `SANDBOXES_SOCKET` задаёт сокет по умолчанию для текущей shell-сессии.

> **Примечание об альфе:** эта страница описывает опубликованный интерфейс CLI. Runtime и daemon содержат exec/PTY пути, а VM-backed lifecycle прошёл live acceptance на macOS ARM64. Полные интерактивные сценарии агентов, Windows WHP, облачные команды и платформенная parity остаются вне области или непроверенными. Независимый внешний security review не проводился. Перед настройкой VM backend прочитайте [системные требования](requirements.md).

## Создание и запуск

```sh
rsbx run shell .
rsbx run --detach --name api --cpus 2 --memory 2g shell .
rsbx create --name api shell . /путь/к/docs:ro
rsbx run --clone shell .
```

`--clone` подключает единственный workspace только для чтения и работает в приватном клоне внутри гостя, отдавая коммиты агента через host-remote `sandbox-<name>`, пока песочница запущена. URL remote содержит случайный токен для каждой песочницы: `git://127.0.0.1:<port>/<token>/<repository>`. Образ должен содержать `git` и `git daemon`, а существующий непустой каталог назначения отклоняется. Жизненный цикл, вид endpoint и ограничения описаны в разделе [workspace и файлы](workspaces.md#clone-mode).

Грамматика CLI определяет `run` как создание или повторное использование песочницы, запуск и подключение оболочки. Runtime и daemon содержат exec/PTY реализацию, а VM-backed проверки lifecycle прошли на macOS ARM64, но полный agent lifecycle ещё не прошёл общую platform acceptance. Текущий каталог используется по умолчанию. `--detach` возвращает управление после запуска; `create` создаёт песочницу без подключения. `rsbx agents list` показывает встроенный реестр агентов, образ, команду запуска и заметки по авторизации.

## Просмотр и управление

```sh
rsbx ls
rsbx get api
rsbx start api
rsbx stop api
rsbx exec -it api /bin/sh
rsbx rm --force api
```

`ls` показывает список песочниц, `get` — подробности, `ports` — опубликованные порты. `start`, `stop` и `rm` принимают несколько имён. `rm` отказывается удалять запущенную песочницу без `--force`. `rm --all` удаляет все песочницы — сначала проверьте список. `rsbx stop` останавливает песочницу; это отдельная команда от `rsbx daemon stop`, которая управляет процессом daemon.

## Машиночитаемый вывод {#machine-readable-output}

`ls`, `rm`, `stop`, `prune`, `secret ls`, `policy ls`, `policy check`, `settings` и `diagnose` принимают `--format table|json|yaml`, а большинство также `--json` как сокращение для JSON. `--json` нельзя комбинировать с явным `--format`. Табличный вывод остаётся по умолчанию и не меняется из-за sbx-совместимых схем.

- `ls --json` выводит массив записей `name`, `id`, `agent`, `status`, `last_used_at`, `workspaces` и `created_at`. `get --json` выводит одну запись с тем же набором полей; `get` — расширение Gyrel.
- `rm --json` и `stop --json` выводят массив записей `{action, resource, name}`. `start` по-прежнему выводит operation records, а не sbx-форму mutation.
- `prune --dry-run --json` выводит `{"would_remove":[...],"skipped_unknown_stop":[...]}`; фактическое удаление prune использует те же записи `{action, resource, name}`, что и `rm`.
- `secret ls --json` использует sbx-envelope инвентаря secrets и никогда не включает значение secret.
- `policy ls --json` выводит `{"rules":[...]}` с `id`, `name`, `policy_id`, `scope`, `applies_to`, `resource_type`, `decision`, `resources`, `origin`, `layer`, `status`, `editable`, `provenance`, `actions` и `sandbox_id` для scoped-правил. `policy check network --json` выводит поля вердикта sbx.
- `settings ls --json` и `settings get --json` выводят типизированные записи: `key`, `value`, `type`, `source`, `default`, `env_var` где он определён, и `requires_restart` при необходимости.
- `diagnose --json` выводит плоский отчёт sbx: `version`, `checks[]` с `name`, `status`, `message`, `detail`, `hint`, и `summary`. `--format github-issue` создаёт Markdown-текст issue со встроенным JSON-отчётом.

Пустые наборы результатов `ls`, `rm`, `stop` и `prune` выводятся как `[]` там, где схема sbx ожидает массив.

## Workspace и файлы

```sh
rsbx run shell . /путь/к/reference:ro
rsbx cp ./input.txt api:/tmp/input.txt
rsbx cp api:/tmp/output.txt ./output.txt
```

Суффикс `:ro` подключает workspace только для чтения. `cp` копирует обычные файлы и каталоги; путь внутри гостя должен быть абсолютным. Реализация отклоняет traversal и неподдерживаемые типы файлов. Символические ссылки по умолчанию запрещены, если явно не включено следование по ссылке.

Пути workspace относятся к host-системе. Подключайте только необходимые агенту каталоги. Если у workspace есть право записи, процессы гостя смогут менять эти файлы host-системы. Суффикс `:ro` запрещает запись через это подключение, но не скрывает файлы внутри образа гостя.

## Переменные среды и секреты

```sh
rsbx exec -e MODE=debug api env
rsbx secret set openai --sandbox api
rsbx secret ls
rsbx secret rm openai --sandbox api
```

Используйте `-e KEY=VALUE` для переменной одной сессии. Значения в аргументах команды могут быть видны в списке процессов host-системы; не передавайте так секреты. `rsbx env plan [PATH...]` создаёт статический preview без изменений. Без путей читает `sbxenv.yaml` из текущего каталога и сначала объединяет необязательные defaults из `~/.sbxenv.yaml`; явно переданные файлы или каталоги объединяются по порядку и пропускают user defaults. YAML-значения поддерживают `${{ env.projectDir }}` и `${{ env.fileDir }}`. Preview показывает объявленные порты, но не открывает их. `args` проверяются через `--env-arg` и `--env-args-file`; значения скрыты в preview. Совокупный объём аргументных данных ограничен 8 MiB, количество значений — 20 000. Значения самого `--env-arg` могут быть видны в списке процессов, поэтому чувствительные значения передавайте через файл аргументов. Ссылки `${{ env.args.NAME }}` подставляются в YAML-значения один раз; аргументы kit пока не реализованы. Флаг `--name NAME` задаёт имя sandbox для preview. `rsbx env create [PATH...]` создаёт локальную песочницу из поддерживаемого набора полей: agent, name, workspace mounts, ports, environment variables, CPU и memory. В терминале команда запрашивает подтверждение; для неинтерактивного запуска используйте `--force`, который подтверждает только этот запуск. `rsbx env run` создаёт отсутствующую песочницу или подключается к существующей с совпадающей конфигурацией; `--detach` запускает её без подключения. `rsbx env exec` выполняет команду в совпадающей существующей песочнице и запускает её, если она остановлена. `rsbx env rm` удаляет только песочницу с совпадающими именем, agent и workspace. Kits, credential bindings, host-команды и MCP-декларации не поддерживаются и отклоняются. Для env lifecycle есть command/unit-test coverage; полная межплатформенная совместимость с Docker и live runtime acceptance ещё не подтверждены. `rsbx run --env` задаёт переменные только для одного запуска/сессии и не заменяет workflow с env-файлами. `rsbx secret` хранит значения провайдеров в host credential vault и не записывает их в SQLite или логи. Перед включением secret proxy прочитайте [модель безопасности](security.md). Вход в Docker account — отдельный сценарий, он описан в [Docker и Gyrel](docker.md).

## Сеть и порты

```sh
rsbx run --publish 127.0.0.1:8080:3000 shell .
rsbx ports api
rsbx policy ls api
rsbx policy org
```

Новые sandboxes по умолчанию используют профиль egress `allow-all`, как и Docker `sbx`: TCP и UDP к `0.0.0.0/0` с учётом явных deny-правил. `deny-all` остаётся доступным через `--policy-profile deny-all`, `rsbx policy init deny-all` или `policy.profile`. Явные deny-правила по-прежнему важнее allow, org deny имеет приоритет над локальными правилами, а все fail-closed контроли не меняются. Песочница с `deny-all` не сможет использовать исходящую сеть, пока правило не разрешит трафик.

Слой политики gateway поддерживает HTTP-условия для method (точный список или `ANY`), path glob и query-параметров, но локальная surface политики `rsbx` пока не содержит этих полей, поэтому в этой альфе `rsbx run` и `rsbx policy` не могут их задать. Там, где такие условия присутствуют, они оцениваются по ограниченному HTTP request head; правило, условия которого не удаётся вычислить, не совпадает и никогда не расширяется до всего назначения. Deny-правила оцениваются раньше allow. Allow и deny с одинаковым selector в одном scope отклоняются типизированной ошибкой конфликта с именами обоих правил. Live-применение HTTP-условий в datapath `gvproxy` остаётся непроверенным, поэтому не считайте HTTP-правило доказанным пакетным фильтром.

`rsbx policy org` показывает действующую организационную политику: org, идентичность bundle, состояние enforcement и каждое правило с пометкой enforced или advisory (таблица или `--format json`). Явные правила поддерживают IPv4 CIDR и домены, если их поддерживает настроенный gateway. Публикация портов ограничена loopback-адресами; внешние host bindings отклоняются. Успешная настройка `--publish` не разрешает гостю исходящие подключения. `rsbx policy check` оценивает сохранённые правила; это не live-запрос к gateway и не доказательство того, что пакет будет пропущен.

## Жизненный цикл daemon {#daemon-lifecycle}

```sh
rsbx daemon start --detach
rsbx daemon status
rsbx daemon log-level
rsbx daemon stop
rsbx daemon restart --detach
```

`rsbx daemon` управляет локальным процессом `sandboxesd`. `start` и `restart` работают на переднем плане, если не передан `--detach`, и принимают `--policy allow-all|balanced|deny-all` для инициализации глобального профиля. `status` показывает live endpoint, версию daemon, версию API, socket и путь логов, а также количество sandboxes; `status --json` использует имена полей sbx `status`, `socket` и `logs` плюс доступные поля PID, версии, API и счётчиков. `log-level` показывает категории `general`, `proxy` и `all`; `log-level set TARGET LEVEL` сохраняет изменение без перезапуска daemon.

Каталог состояния и путь логов выводятся из `--socket`. CLI передаёт daemon `--state` и `--socket`, находит `sandboxesd` в `PATH` или рядом с `rsbx`; переменная `SANDBOXES_DAEMON_BINARY` задаёт другой бинарник. Daemon, запущенный отдельно с явными runtime-флагами VM, как в [быстром старте](quickstart.md), сохраняет собственный жизненный цикл процесса. `rsbx daemon stop` и `rsbx daemon restart` применяют описанные ниже проверки идентичности; если control record не идентифицирует этот daemon, а платформа не умеет определять socket peer, команда сообщает неоднозначное состояние, а не угадывает.

`rsbx daemon stop` сигналит только тому daemon, чью идентичность удалось доказать. Daemon, запущенный вне `rsbx daemon start`, останавливается, если его идентичность доказана по live socket peer. Если доказать её нельзя, stop отказывается сигналить и печатает actionable-сообщение: проверьте процесс, владеющий socket, остановите его вручную через `SIGTERM` и проверьте endpoint перед удалением. На платформах, где определить socket peer невозможно, команда решает по control record. `restart` использует те же проверки перед запуском нового daemon. Устаревшие socket и control records не удаляются молча.

## Docker

CLI принимает `--docker` для опционального профиля Docker внутри guest. Профиль может запустить `dockerd`, но вложенные `docker run/load/build` и Compose пока блокируются ограничениями `unshare` в текущем runtime. Это не означает, что VM не запускается. `rsbx login` сохраняет авторизацию Docker account на host-системе, но не передаёт registry credentials в гостевую среду. Актуальный статус и история описаны в [руководстве Docker](docker.md).

## Настройка хоста и вспомогательные команды {#host-setup-and-helpers}

```sh
rsbx setup
rsbx skills list
rsbx skills import ./my-skill
rsbx completion zsh
```

`setup` — read-only отчёт о готовности хоста (платформа, сокет daemon, runtime-ассеты, нужные бинарники, Docker CLI) с `--format json`; он ничего не устанавливает и не утверждает, что VM загрузится. `setup` и `skills` по-прежнему помечены в справке как экспериментальные. `skills` управляет host-side источниками skills агентов (`list`, `import`, `remove`) и никогда не пишет в workspace песочницы. `import` без пути просматривает шесть поддерживаемых каталогов агентов, `--dry-run` показывает кандидатов. `rsbx run --skills=readonly` или `rsbx create --skills=readonly` подключает store к новой песочнице только для чтения; `readwrite` отвергается до появления безопасного целевого каталога, а гостевая доставка ещё не квалифицирована на всех платформах. `completion` печатает скрипт для bash, zsh, fish или powershell.

Облачные команды (`move`, `ttl`, `volume`) вне области локальной альфы и остаются неподдерживаемыми. Windows WHP не реализован.

## Точная справка

Используйте встроенную справку установленной версии:

```sh
rsbx --help
rsbx run --help
rsbx policy --help
rsbx daemon --help
```

Продукт находится в стадии alpha, поэтому флаги и поведение могут меняться между выпусками. Перед использованием команды проверьте справку установленного бинарника.
