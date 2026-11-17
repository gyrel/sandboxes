# Сравнение с Docker `sbx`

## Область и метод

Снимок сравнивает **Docker `sbx` v0.50.1** на macOS ARM64 (`/opt/homebrew/bin/sbx`, SHA-256 `a1e506d1b1f2e17bbc54a3b8e9850592860777689fe3f49098be6279b728c45e`) и **Rheic `rsbx` v0.0.54** (`rsbx-darwin-arm64`, SHA-256 `c3aad0a1fbfd3dc497cdaf1bfe55a659a629f9f34139be4a3bd5cb0421124841`). 17 ноября 2026 года сняты `--help` верхнего уровня и 27 одинаковых команд; версии и release checksums проверены отдельно. Это **evidence поверхности CLI**, а не живое сравнение одинаковых сценариев. При проверке sandbox не создавались и не удалялись.

| Сценарий | Docker `sbx` v0.50.1 | Rheic `rsbx` v0.0.54 | Статус |
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

**Одинаковое имя команды не доказывает parity.** Нужны одинаковые входные данные, флаги, prompts, exit codes, guest-visible state и cleanup. Границы runtime приведены в [ограничениях](limits.md). Rheic использует имя `rsbx` и не занимает Docker `sbx`.

## Следующие проверки

1. Изолированное временное состояние, уникальные sandbox-имена и synthetic credentials.
2. Одинаковые положительные и отрицательные сценарии на одной ОС/архитектуре с фиксацией результата и side effects.
3. Исправление каждого разрыва кодом и contract tests; parity отмечать только после прохождения controls.
