# Справочник CLI

Выпущенная пользовательская команда — `rsbx` v0.0.54. Она работает с локальным `sandboxesd`. Точные флаги установленной версии показывает `rsbx COMMAND --help`.

## Основной сценарий

```sh
rsbx version
rsbx run shell .
rsbx ls
rsbx get NAME
rsbx stop NAME
rsbx start NAME
rsbx exec NAME -- /bin/sh
rsbx rm NAME
```

`run` создаёт, запускает и подключает. По умолчанию workspace — текущий каталог; `--detach` выходит после запуска. Аргументы агента идут после `--`. `--name` выбирает именованный sandbox; `--new` всегда создаёт новый, `--replace` пересоздаёт именованный. `--clone` создаёт приватный clone локального Git root в госте. Дополнительные пути поддерживают `:ro`; `--deny-write PATH` добавляет read-only subpath.

`create` отличается от `run`: без пути он создаёт sandbox **без** workspace mount. Проверяйте команду до передачи агенту доступа к файлам.

| Область | Выпущенные команды | Граница |
|---|---|---|
| Sandbox | `run`, `attach`, `create`, `exec`, `cp`, `ls`, `get`, `start`, `stop`, `rm`, `prune`, `wait`, `ports` | Только локальный daemon |
| Управление | `agents`, `daemon`, `diagnose`, `env`, `login`, `logout`, `mcp`, `policy`, `reset`, `secret`, `settings`, `tui` | Не все подкоманды Docker доступны |
| Расширения | `kit`, `template`, `skills`, `setup` | Локальные kits; template inspect/list; `setup` только читает |
| Cloud | `move`, `ttl`, `volume` | Явно не поддерживаются |

`--policy-profile` по умолчанию `allow-all`; для более узкого egress задайте профиль явно. Host hooks и secrets требуют отдельного решения о доверии. См. [ограничения](limits.md) и [сравнение с Docker](comparison.md).
