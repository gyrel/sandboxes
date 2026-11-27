# Сравнение с Docker `sbx`

Эта страница фиксирует, для каких частей поверхности CLI Docker `sbx` и Gyrel `rsbx` есть записанный контроль, а какие остаются `unverified`.

## Область и метод

Сравнение охватывает Docker `sbx` v0.50.1 и Gyrel `rsbx` CLI 0.0.81 на macOS ARM64. SHA-256 закреплённых бинарников: `a1e506d1b1f2e17bbc54a3b8e9850592860777689fe3f49098be6279b728c45e` для sbx и `085ec502869ff6c86efacca84af8078a20bd1367f929af496ce007578a1b8669` для rsbx. В release record этой CLI соответствуют daemon 0.0.104 и контракт API 0.0.38. Проба проверяла только бинарник CLI.

Контроли записаны 2026-11-27 на macOS ARM64. Оба бинаря запускались с `--help` верхнего уровня и отдельных команд. Проба также запускала `version`, `--version` и пути ошибок валидации аргументов. Песочницы не создавались, daemon не запускался, аутентификация не выполнялась. Evidence поверхности не доказывает runtime parity.

## Словарь статусов

| Статус | Значение |
|---|---|
| `parity` | Одинаковые входные данные дали одинаковый записанный результат на обоих бинарях. В этой пробе статус не используется. |
| `partial` | Часть поведения поверхности записана; пробелы перечислены в той же строке. |
| `differs` | Записанное намеренное расхождение; причина указана в строке. |
| `gap` | Не реализовано; принятое ограничение альфы. |
| `unverified` | Реализовано или присутствует, но записанного контроля нет. |

## Сравнение

| Slug | Область | sbx v0.50.1 | rsbx (CLI 0.0.81 / daemon 0.0.104) | Статус | Какие evidence ещё нужны | Закрывает |
|---|---|---|---|---|---|---|
| `run` | run | Help верхнего уровня и `run` сверен. Cloud-флаги включают `--detach-keys` у `run`, `--ttl` и `--volume`. | Локальная грамматика. `--detach-keys` у `run` отсутствует; `--template` — алиас `--image`; `--kit` принимает одну строку. | unverified | E1 одинаковый запуск create, attach и exec; E3 для некорректных входных данных | — |
| `create` | create | Полный набор флагов, включая cloud `--image-ref`, `--profile`, `--mount`, `--ttl` и `--volume`. | `--image` заменяет `--image-ref`; `--policy-profile` заменяет `--profile`; `--kit` одиночный; `--skills readwrite` не поддерживается; добавлены `--deny-write`, `--docker` и `--idempotency-key`. | partial | E2 атомарность при kill; E3 для `NAME_INVALID` и `AUDIT_CAP_EXCEEDED`; E1 корпус грамматики | CR-1…CR-5 |
| `exec` | exec | Полный набор флагов, включая `--privileged` и `--detach-keys`. | Набор флагов совпадает. Локальный runtime отклоняет `--privileged`; `--detach-keys` доступен только для cloud. | partial | E3 для 125, 126 и 127, а также для `APPROVAL_PROVIDER_UNAVAILABLE`; E1 фикстура кодов выхода; живой PTY остаётся `gap` | EX-1…EX-6 |
| `cp` | cp | `-L/--follow-link` следует по symlink и отклоняет выход за пределы workspace. | `-L/--follow-link` следует по symlink верхнего уровня; вложенные ссылки отклоняются. | partial | E3 для `MEMBER_TYPE_REFUSED`, `LINK_ESCAPE` и `HOST_PATH_NOT_ALLOWED`; E2 откат по tree hash | CP-1…CP-6 |
| `ls` | ls | `--format`, `--json` и `-q/--quiet`. | Те же флаги; добавлен `--limit` (1–1000). | partial | E2 фикстура JSON schema; E3 для состояния `unknown` при недоступном daemon; byte-grep маскирования | LS-1…LS-4 |
| `stop` | stop | `--format` и `--json`. | Те же флаги; добавлен `--grace`. | unverified | E1 цикл stop/start; E3 для `NOT_OWNED` и `SESSION_UNREAPED`; E2 освобождение порта | SR-1…SR-6 |
| `rm` | rm | `--all`, `-f/--force`, `--format` и `--json`. | Те же флаги. Без `--force` все указанные песочницы должны быть остановлены, иначе не удаляется ничего. | unverified | E3 отказ по каждому элементу; E2 tree diff с одним удалением; E1 повторный rm | SR-1, SR-2, SR-5 |
| `prune` | prune | `--filter stringArray` (повторяемый), `--dry-run`, `-f/--force`, `--format` и `--json`; секреты очищаемых песочниц удаляются. | `--filter string` (один); `until=TIMESTAMP` или `until=DURATION`; остальные флаги те же; очистка секретов не описана. | unverified | E3 для четырёх классов `UNCLASSIFIED`; E2 hash всего дерева при abort; E1 diff плана dry-run и реального запуска | PR-1…PR-8 |
| `ports` | ports | `[[HOST_IP:]HOST_PORT:]SANDBOX_PORT[/PROTOCOL]`; описаны tcp4 по умолчанию, dual-stack loopback и правила cloud. | `[[HOST_IP:]HOST_PORT:]GUEST[/tcp\|udp\|tcp4\|udp4\|tcp6\|udp6]`; правила протокола по умолчанию и loopback не описаны; раздела cloud нет. | partial | E1 для 6 канонических и 10 некорректных спецификаций; E2 фикстура таблицы резервирований; E3 для `PORT_IN_USE`, `PORT_RESERVED`, `BIND_FORBIDDEN` и `POLICY_DENY` | PT-1…PT-6 |
| `kits` | kits | `--kit strings` (повторяемый); локальный каталог, ZIP, Git и OCI; mixins и аргументы kit. | `--kit string` (один локальный kit); remote OCI и mixins отсутствуют. | unverified | E1 корпус жизненного цикла kit | — |
| `cloud` | cloud backend | `--cloud`, `move`, `ttl` и `volume`. | `--cloud` отсутствует. `move`, `ttl` и `volume` зарегистрированы, но возвращают `unsupported` с кодом 1. | gap | Нет. Принятое ограничение альфы, указано в [ограничениях](limits.md). | non-goal |
| `template` | шаблоны | `inspect`, `load`, `ls`, `rm` и `save`. | Те же подкоманды плюс `export`. | partial | E4 запись для roundtrip P1.5; E1 крайние случаи whiteout | — |
| `mcp` | MCP | `add`, `auth`, `inspect`, `load`, `ls`, `rm` и `unload`. | Те же подкоманды плюс `call`. | partial | E1 add, list, call и remove; E3 для пробела literal-header | non-goal для пробела заголовка |
| `policy-approval` | policy approval | `policy approval` указан с `inspect`, `ls` и `respond`. | `policy approval` сохранён, но скрыт; документированная поверхность — `policy org`. Формы `inspect`, `ls` и `respond` совпадают. | differs | E3 код отказа fail-closed; E1 путь challenge | EX-2 |
| `secret` | secrets | `import`, `ls`, `rm`, `set` и `set-custom`; алиас `secrets`. | Те же подкоманды и алиас. | partial | E3 отклонение команды-источника; X-3 маскирование путей vault и вывода `ls` | LS-3, X-3 |
| `settings` | settings | `get`, `ls`, `set` и `unset`. | Те же подкоманды; описаны `~/.config/rheic/settings.toml` и формат записи settings из sbx. | partial | E1 по полному списку имён settings из sbx; E3 для `SETTINGS_INVALID` | X-5 |
| `tui` | TUI | Команда `tui`. | Команда `tui` присутствует в help верхнего уровня. | unverified | E1-эквивалент со скриптовым терминалом (журнал клавиш и дамп кадров); LS-4 | LS-4 |
| `login-logout` | login/logout | `login` и `logout` в разделе Other. | `login` и `logout` в разделе Management. | unverified | E4 запись для одинакового контроля login/logout; E3 для пробела с именем аккаунта | — |
| `help-layout` | формат help | Секции Cobra: Sandbox, Management, Experimental, Other. Неизвестная команда с `--help` печатает help ближайшего предка и выходит с кодом 0. | Добавлена секция Unsupported Docker Sandboxes Commands. `template` переходит в Experimental; `env`, `login` и `logout` переходят в Management; `agents` есть только в rsbx. Неизвестная команда с `--help` выходит с кодом 1. | differs | E4 запись с обоими SHA и артефактом diff для любого утверждения parity | — |
| `policy-ls` | policy ls | `policy ls` выводит правила allow по умолчанию в таблице `POLICY / SOURCE / APPLIES TO / SUMMARY`. | `policy ls` присутствует; вывод базовых правил не записан. | unverified | E4 запись с закреплённой фикстурой базовых правил | — |

Две строки имеют статус `differs` по записанному различию поверхности. `policy-approval` сохраняет `policy approval` скрытой командой и документирует вместо неё `policy org`. `help-layout` использует строгую обработку неизвестных команд: неизвестная команда с `--help` выходит с кодом 1, а не печатает help предка.

## Защита от побочных эффектов

Бывшая общая строка `create`–`ports` разделена по slug. Проба сравнила грамматику флагов и подкоманд, вывод версии и пути ошибок валидации аргументов. Она не проверяла создание песочницы, состояние гостевой среды, очистку, резервирование портов и применение policy.

Защита от побочных эффектов в работе: готовятся guards B0/B1. Ни один контроль этой пробы их не проверяет. Контроли будут записаны по E4 до перехода строки выше `partial`.

**Одинаковое имя команды не доказывает parity.** Совпадающее имя команды или флага не доказывает совпадение поведения. Флаги, prompts, коды выхода, guest-visible state и очистка требуют одинаковых живых контролей. Границы runtime приведены в [ограничениях](limits.md). `rsbx` — бинарник Gyrel; он не занимает имя Docker `sbx`.

## Evidence и ограничения

Все контроли записаны 2026-11-27. Сырые записи лежат в `/tmp/rheic-gyrel-20261127/probe-logs/`. Манифест — `/tmp/rheic-gyrel-20261127/EXECUTOR-REPORT-PROBE.md`. Пути артефактов ниже указаны относительно каталога записей.

### E1 — одинаковые входные данные поверхности

| Контроль | Область | Артефакт |
|---|---|---|
| Control 1 | `version` и `--version` на обоих бинарях, с SHA-256 | `00-control1-version-sha.txt` |
| Control 2 | Инвентаризация секций `--help` верхнего уровня | `01-sbx-help.txt`, `02-rsbx-help.txt` |
| Control 3 | Пофлаговая сверка для 8 команд | `sbx-*-help.txt`, `rsbx-*-help.txt` |
| Control 4 | Management-команды: template, mcp, policy, secret, settings, agents | `sbx-{template,mcp,policy,secret,settings}-help.txt`, `rsbx-{template,mcp,policy,secret,settings,agents}-help.txt` |
| Control 5 | Грамматика `prune --help` | `sbx-prune-help.txt`, `rsbx-prune-help.txt` |
| Control 6 | Грамматика `ports` | `sbx-ports-help.txt`, `rsbx-ports-help.txt` |
| Control 7 | `run --detach` и detach keys | `sbx-run-detach-help.txt`, `rsbx-run-detach-help.txt` |

### E3 — отрицательные контроли

| Контроль | Область | Артефакт |
|---|---|---|
| Control 8 | Неизвестные команды, документированные алиасы, неподдержанные команды | `09-exit-codes.txt` |
| Control 9 | Матрица кодов выхода для пропущенных аргументов, неизвестных флагов и команд | `09-exit-codes.txt` |

### E2 — проверки состояния

Нет записей. Проба не меняла файловую систему и состояние гостевой среды.

### E4 — записи ledger

Записей пока нет. Этот раздел — манифест для заполнения ledger. Каждая запись требует id контроля, дату, runner identity, версии и SHA обоих компонентов, пару команд и путь к артефакту.

### Ожидаемые контроли

Этих контролей пока нет. Строки, которым они нужны для более сильного статуса, остаются `partial` или `unverified`.

- E2 проверки состояния: атомарность `create`, откат `cp`, JSON schema `ls`, освобождение порта `stop`, tree diff `rm`, hash при abort `prune`, таблица резервирований `ports`.
- E3 коды отказа по командам: `create` `NAME_INVALID` и `AUDIT_CAP_EXCEEDED`; `exec` 125, 126, 127 и `APPROVAL_PROVIDER_UNAVAILABLE`; `cp` `MEMBER_TYPE_REFUSED`, `LINK_ESCAPE` и `HOST_PATH_NOT_ALLOWED`; `stop` `NOT_OWNED` и `SESSION_UNREAPED`; `ports` `PORT_IN_USE`, `PORT_RESERVED`, `BIND_FORBIDDEN` и `POLICY_DENY`; `secret` отклонение команды-источника; `settings` `SETTINGS_INVALID`.
- E1 runtime-контроли: цикл create, attach и exec для `run`; жизненный цикл `kits`; скриптовый терминал `tui`; одинаковый запуск `login` и `logout`; фикстура `policy ls`; путь challenge `policy-approval`; артефакт diff `help-layout`.

Строки, которые зависят от этих отсутствующих контролей и остаются `unverified`: `run`, `stop`, `rm`, `prune`, `kits`, `tui`, `login-logout`, `policy-ls`. Строки `partial` перечисляют свои пробелы на месте и не заявляют parity. `policy-approval` и `help-layout` имеют статус `differs` по записанному различию поверхности. Их runtime-поведение остаётся unverified.

Сессии агентов и аутентифицированные контроли Codex вне этой пробы. Текущие ограничения — в [агентах](agents.md) и [ограничениях](limits.md).
