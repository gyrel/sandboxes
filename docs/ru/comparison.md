# Сравнение с Docker `sbx`

## Область и метод

Снимок сравнивает **Docker `sbx` v0.50.1** на macOS ARM64 (`/opt/homebrew/bin/sbx`, SHA-256 `a1e506d1b1f2e17bbc54a3b8e9850592860777689fe3f49098be6279b728c45e`) и **Rheic `rsbx` v0.0.58** (`rsbx-darwin-arm64`, SHA-256 `eb05f27aac36fa212a436689a7961390bba369ea61f03c928586194a1562f1ec`). 17 ноября 2026 года сняты `--help` верхнего уровня и 27 одинаковых команд; версии и release checksums проверены отдельно. Это **evidence поверхности CLI**, а не живое сравнение одинаковых сценариев. При проверке sandbox не создавались и не удалялись.
> Это сохранённый снимок поверхности CLI v0.0.58. Актуальные релизы — CLI v0.0.64 и daemon v0.0.72; перед переносом любой строки на текущее поведение повторите те же контроли.


| Сценарий | Docker `sbx` v0.50.1 | Rheic `rsbx` v0.0.58 | Статус |
|---|---|---|---|
| Локальный `run [agent] [path]` | Создаёт или повторно использует и подключает; `--detach`, workspaces и аргументы после `--` | Та же базовая грамматика и цель; нужен локальный daemon | Help сравнен; одинаковый runtime probe открыт |
| `create`, `exec`, `cp`, `ls`, `stop`, `rm`, `prune`, `ports` | Есть | Есть | Help сравнен; полные side effects не проверены |
| Kit references в `run` | Локальный каталог, ZIP, Git, OCI; mixins и kit arguments | Локальный kit через `--kit`; remote OCI и mixins отсутствуют | Подтверждённое расхождение CLI |
| Cloud `--cloud`, `move`, `ttl`, `volume` | Cloud-пути есть | Cloud backend отсутствует; неподдержанные команды возвращают ошибку | Подтверждённый продуктовый пробел |
| `template` | List, inspect, save, load, remove | Только list и inspect встроенных шаблонов | Подтверждённое расхождение CLI |
| `mcp` | Add, auth, inspect, load, list, remove, unload | List, add, call, remove | Подтверждённое расхождение CLI |
| `policy approval` | Команды approval есть | Явный fail closed как unimplemented | Подтверждённое расхождение CLI |
| `secret` | Service/registry flows, в том числе custom values | Import, list, set, remove; custom secret values отсутствуют | Подтверждённое расхождение CLI |
| `settings` | List, get, set, unset | Те же имена; сохраняется проверяемое локальное подмножество | Help сравнен; значения и side effects открыты |
| Interactive TUI и agent sessions | Есть | TUI и preview agents доступны | Interactive parity открыт |
| `login` / `logout` | Device code, вход в браузере, `Signed in as <user>.`; повторный login сообщает о существующей сессии | Тот же device flow, тексты, подсказки и коды после фикса в v0.0.55; имя аккаунта пока не выводится | Живое сравнение и проверки релизным бинарём пройдены |
| Поверхность команд | `start`, `get` и `wait` — unknown command; у `ls`/`rm`/`secret` есть документированные алиасы | Так же: лишние команды удалены в v0.0.57, алиасы восстановлены | Живое сравнение пройдено |
| Формат `--help` | Cobra-секции с полной таблицей флагов | Тот же layout для всех команд, только реализованные флаги | Отрисовано и сверено |
| `policy ls` | Дефолтные allow-правила в таблице `POLICY / SOURCE / APPLIES TO / SUMMARY` | Тот же базис для `allow-all` и та же таблица; строка kit-политики песочницы отсутствует | JSON сверен по полям для базовых правил |

**Одинаковое имя команды не доказывает parity.** Нужны одинаковые входные данные, флаги, prompts, exit codes, guest-visible state и cleanup. Границы runtime приведены в [ограничениях](limits.md). Rheic использует имя `rsbx` и не занимает Docker `sbx`.

## Живая проверка Codex: signed-out controls

17 ноября 2026 года оба бинаря проверены на macOS ARM64 с новым приватным состоянием, пустым workspace, уникальным именем и без пользовательских credentials. `sbx run --detach codex` и `sbx create codex` завершились с exit 1 до создания sandbox: `not signed in to Docker`. Rheic `rsbx run --detach codex` завершился с exit 1 после OpenAI OAuth без полученных credentials. Rheic `rsbx create codex` дошёл до pinned Codex template image, но анонимный запрос manifest в Docker Hub получил `401 Unauthorized`. Собственные имена отсутствовали после пробы; временные daemon и containerd остановлены.

Это **отрицательное живое сравнение**, а не завершённая сессия Codex. Порядок prerequisites и ошибок различается. Успешная guest task на одинаковых входных данных остаётся непроверенной: Docker sign-in и доступ к закреплённому образу требуют аутентификации, а реальные пользовательские credentials в пробе не использовались.

## Следующие проверки

1. Изолированное временное состояние, уникальные sandbox-имена и synthetic credentials.
2. Одинаковые положительные и отрицательные сценарии на одной ОС/архитектуре с фиксацией результата и side effects.
3. Исправление каждого разрыва кодом и contract tests; parity отмечать только после прохождения controls.

## Codex после входа: подтверждённый разрыв

С согласия владельца аккаунта 17 ноября 2026 года на macOS ARM64 проверены одинаковые пустой workspace и запрос. Docker `sbx v0.50.1` запустил Codex, показал `codex-cli 0.165.0`; `codex exec --skip-git-repo-check` вернул `RHEIC_CODEX_PARITY_OK` с кодом 0. Rheic `rsbx v0.0.54` с локально собранным daemon из исходников `v0.0.62` и ещё не влитой поправкой Keychain, а также released native runtime `v0.0.36`, запустил тот же образ и ту же версию Codex. Вход OpenAI в браузере и обмен токенов прошли, но Codex сообщил `Not logged in`; одинаковый запрос получил HTTP `401 Unauthorized` от OpenAI Responses. Явная ссылка на OAuth proxy при `rsbx exec` дала тот же 401. Это **подтверждённое расхождение авторизации**, не parity. Поправка размера Keychain, от которой зависел тот прогон, вошла в CLI v0.0.56 и daemon v0.0.64, но путь авторизации Codex в госте на паре v0.0.58 не перепроверялся, поэтому расхождение остаётся открытым.

Первая попытка Rheic также получила DNS `REFUSED`: у изолированного daemon не был задан DNS upstream при включённой egress policy. После перезапуска собственного sandbox с `-dns-upstream 1.1.1.1:53` DNS заработал, и проявился независимый 401. Для запуска proxy route к released daemon пришлось отдельно собрать guest proxy helper. Поправка Keychain сохранила длинную запись OpenAI в host vault, но ещё не влита и не выпущена. Значения токенов не сохранялись в evidence. Оба собственных sandbox удалены; чужие Docker sandbox не затронуты. Успешная авторизованная задача Codex в Rheic остаётся блокером релиза.
