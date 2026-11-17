# Справочник CLI

Выпущенная пользовательская команда — `rsbx` v0.0.58. Она работает с локальным `sandboxesd`. Точные флаги установленной версии показывает `rsbx COMMAND --help`.

## Основной сценарий

```sh
rsbx version
rsbx run shell .
rsbx ls
rsbx stop NAME
rsbx exec NAME -- /bin/sh
rsbx rm NAME
```

`run` создаёт, запускает и подключает. По умолчанию workspace — текущий каталог; `--detach` выходит после запуска. Аргументы агента идут после `--`. `--name` выбирает именованный sandbox; `--new` всегда создаёт новый, `--replace` пересоздаёт именованный. `--clone` создаёт приватный clone локального Git root в госте. Дополнительные пути поддерживают `:ro`; `--deny-write PATH` добавляет read-only subpath.

`create` отличается от `run`: без пути он создаёт sandbox **без** workspace mount. Проверяйте команду до передачи агенту доступа к файлам.

| Область | Выпущенные команды | Граница |
|---|---|---|
| Sandbox | `run`, `attach`, `create`, `exec`, `cp`, `ls`, `stop`, `rm`, `prune`, `ports` | Только локальный daemon |
| Управление | `agents`, `daemon`, `diagnose`, `env`, `login`, `logout`, `mcp`, `policy`, `reset`, `secret`, `settings`, `tui` | Не все подкоманды Docker доступны |
| Расширения | `kit`, `template`, `skills`, `setup` | Локальные kits; template inspect/list; `setup` только читает |
| Cloud | `move`, `ttl`, `volume` | Явно не поддерживаются |

`--help` использует ту же структуру секций, что Docker `sbx` (`Description`, `Usage`, `Aliases`, `Examples`, `Flags`), и работают документированные алиасы: `list`, `remove`, `delete`, `secrets`. В Docker `sbx` нет `start`, `get` и `wait`; мы убрали свои, чтобы поверхность совпадала, а `run`/`exec` сами стартуют остановленную песочницу. `rsbx policy ls` показывает эталонные базовые правила для `allow-all` (`default-allow-all`, filesystem read/write) в таблице `POLICY / SOURCE / APPLIES TO / SUMMARY`.

`--policy-profile` по умолчанию `allow-all`; для более узкого egress задайте профиль явно. Host hooks и secrets требуют отдельного решения о доверии. См. [ограничения](limits.md) и [сравнение с Docker](comparison.md).
