# OpenCode

OpenCode — встроенный агент со статусом **preview** в выпущенном CLI. Он
использует закреплённый Docker-шаблон и не требует отдельного образа для
первого запуска.

## Проверить наличие

```sh
rsbx agents ls
rsbx agents ls --format json
```

`opencode` должен быть в списке со статусом `preview`. Если его нет, установлен
старый CLI; обновите его, а не копируйте конфигурацию из другой установки.

## Сохранить ключи провайдеров

OpenCode поддерживает несколько провайдеров. Сохраняйте только нужные ключи;
Gyrel сам добавит proxy-ссылки для соответствующих сервисов:

```sh
rsbx secret set openai
rsbx secret set anthropic
rsbx secret set google
rsbx secret set groq
rsbx secret set mistral
rsbx secret set openrouter
rsbx secret set xai
```

Команда запрашивает значение, поэтому ключ не попадает в history.
`rsbx secret ls` показывает сервисы без значений. Явный
`--env OPENAI_API_KEY=...` (или переменная другого провайдера) переопределяет
proxy-ссылку для этого запуска.

## Запустить OpenCode

```sh
# Current directory as the workspace, attach to the agent
rsbx run opencode .

# Named detached sandbox, then attach later
rsbx run --detach --name oc opencode .
rsbx run --name oc opencode .

# Pass an argument to the agent after --
rsbx run opencode . -- --help
```

Встроенная запись сама включает Docker-профиль, нужный шаблону OpenCode.
Read-only workspace добавляется через `:ro`, приватный clone — через
`--clone`. Общие skills можно подключить только для чтения через
`--skills=readonly` (ограничения платформы — на странице CLI).

## Если OpenCode нет во встроенном наборе

Сначала проверьте версию:

```sh
rsbx version
```

Для CLI без встроенной записи зарегистрируйте локального custom-агента в
`~/.config/rheic/agents.yaml` (или в файле из `RHEIC_AGENTS_FILE`):

```yaml
agents:
  - name: opencode
    image: docker.io/docker/sandbox-templates@sha256:f36f91fef60ee2035fe07a5467cf00409d6301071ed790aa0c80c91f5c958d68
    command: ["opencode"]
    status: preview
    docker: true
    notes: Pinned Docker sandbox template; host proxy credentials are configured by the CLI.
```

Используйте образ, закреплённый по digest. Custom-агент не может затенять
встроенное имя; если `opencode` уже встроен, запись с тем же именем
игнорируется. Перезапустите CLI и проверьте `rsbx agents ls`.

## Если что-то не работает

- **Образ не скачивается:** выполните `rsbx login` или переопределите образ
  для контролируемого локального теста через `--image`.
- **Ошибка провайдера:** проверьте `rsbx secret ls`, затем передайте ключ
  явно через `--env`, чтобы изолировать proxy-путь. Не вставляйте ключи в
  history.
- **Не та команда агента:** запускайте `rsbx run --name NAME opencode .`, а
  аргументы агента передавайте после `--`.
- **Проблемы VM или Docker workload:** OpenCode не меняет документированные
  ограничения runtime; nested Docker workloads и полная Docker `sbx` parity
  остаются неквалифицированными.
