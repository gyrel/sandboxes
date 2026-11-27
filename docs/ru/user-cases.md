# Пользовательские кейсы

Эти сценарии выполняются против alpha bundle на macOS ARM64 и показывают точные команды с ожидаемым поведением — включая места, где альфа намеренно отказывает. Команды предполагают `rsbx` и сокет daemon по умолчанию; каталог состояния — `$HOME/.sandboxes` (переопределяется через `GYREL_STATE_DIR`).

## Песочница для ревью проекта

```sh
cd ~/code/my-project
rsbx run shell .
```

`run` создаёт или переиспользует песочницу для текущего каталога, запускает VM и подключает гостевой шелл. Проект смонтирован read-write по тому же пути внутри гостя. Выход из шелла — `Ctrl-D`; песочница продолжает работать, пока вы её не остановите.

```sh
rsbx ls -q
rsbx stop <name> && rsbx rm -f <name>
```

Отдельный запуск + скриптовая сессия:

```sh
rsbx run --detach --name review shell .
rsbx exec review -- git status --short
rsbx exec review -- sh -c 'cargo test 2>&1 | tail -5'
```

Остановленная песочница автоматически стартует при следующем `exec`.

## Работа с агентом

```sh
rsbx run codex .
rsbx run claude ~/code/my-project
```

Сессии агентов читают credentials провайдера из хостового хранилища; гость получает только placeholder-ссылку. Этот путь — preview: launch-пробы прошли, полная провайдерская аутентификация по каждому агенту не квалифицирована — см. [агенты](agents.md).

## Один проект для нескольких агентов

```sh
rsbx run --name alice claude ~/code/my-project
rsbx run --name bob codex ~/code/my-project
```

Каждая песочница получает свою VM и свой взгляд на workspace; общего записываемого состояния нет, если вы явно не монтировали workspace. Изоляция между VM прошла live acceptance.

## Копирование файлов

```sh
rsbx cp ./patch.diff review:/tmp/patch.diff
rsbx exec review -- git -C $PWD apply --check /tmp/patch.diff
rsbx cp review:/tmp/report.html ./report.html
```

`cp` работает в обе стороны и отказывается проходить через symlink-выходы на границе.

## Публикация порта

```sh
rsbx run --detach --name web shell .
rsbx run -p 8080 --name web2 shell .    # or `-p 8080:3000` for a fixed pair
rsbx ports web
```

Gateway публикует хост-порты на `127.0.0.1`. Публикация занятого порта падает с понятным конфликтом и ничего не меняет.

## Заморозка окружения в шаблон

```sh
rsbx run --detach --name lab shell .
rsbx exec lab -- sh -c 'pip install pandas==2.2.3'
rsbx stop lab
rsbx template save lab pandas-lab
rsbx template ls
rsbx template export pandas-lab ./pandas-lab.tar
```

Шаблоны — это OCI layer diffs с семантикой whiteout и opaque-директорий; экспортированные архивы никогда не содержат файлы вашего хост-workspace. Запуск `rsbx run --image docker.io/library/pandas-lab:v1 …` переиспользует локальный образ без pull из реестра. При сохранении выдается предупреждение о credentials, оставшихся в гостевой файловой системе.

## Credentials в хостовом хранилище

```sh
rsbx secret set openai                       # interactive paste, value stays on host
rsbx secret ls
rsbx secret set-custom --host api.example.com --env API_KEY
```

`set-custom` печатает сгенерированный placeholder один раз, чтобы вы могли прописать его в конфиги; `secret ls` показывает только маску на конце. Инлайновые значения не попадают в логи daemon и в базу состояния. `rsbx secret rm` удаляет запись хранилища и инвалидирует последующую подстановку — незавершенный запрос доходит, следующие — нет.

Sources со ссылками и командами (`--ref op://…`, `--command /usr/local/bin/token-helper`) создают запрос согласия вместо сохранения, и предоставление ждет доверенный OS-backed approval — поэтому сегодня `approve` честным образом fail-closed.

## Просмотр запросов согласия

```sh
rsbx mcp add docs --url https://mcp.example.com/mcp
rsbx policy approval ls
rsbx policy approval inspect <ID>
rsbx policy approval respond <ID> --option deny
```

Регистрация MCP отвечает challenge-ID и ничего не хранит до согласия. `inspect` показывает host/path назначения, имена заголовков и их vault-классификацию — никогда значения. Одобрение требует OS-backed consent provider (в работе); отказ работает всегда и протоколируется.

## Декларативный kit

```sh
mkdir my-kit && cat > my-kit/spec.yaml <<'YAML'
apiVersion: gyrel.dev/v1alpha1
kind: Kit
metadata:
  name: my-kit
spec:
  agent: shell
YAML
rsbx kit validate ./my-kit --offline
rsbx kit pack ./my-kit
```

`pack` пишет детерминированный ZIP (сортированные записи, зафиксированные timestamps, без symlink, без перезаписи). Без `--offline` валидация дополнительно прогоняет daemon-политику kit (`kit.allowedSources`, `kit.allowLocalKits`, `kit.requireSignature`) и печатает, какой ключ решил отказ.

## Проверка сетевой политики

```sh
rsbx policy allow network api.openai.com --sandbox web
rsbx policy check network api.openai.com --method GET --sandbox web
rsbx policy ls web
```

`check` вычисляется по сохраненным правилам и говорит allow/deny, не трогая сеть. Deny имеет приоритет; org-managed правила могут только ужесточать локальные.

## Живые события в терминале

```sh
rsbx tui
```

Нажмите `2` для потока событий (прогресс операций и смены жизненного цикла) и `3` для логов песочницы. Панели показывают ограниченный хвост со счётчиком отброшенного; переключение панели отменяет базовый стрим.

## Восстановление после жесткого убийства процесса

```sh
kill -9 <daemon-pid>          # abrupt loss, like a crash
bin/gyreld-launch.sh          # next start reconciles automatically
```

При старте daemon примиряет create-журналы: ресурсы, владение которыми доказуемо (совпадение token-маркера), дочиста убираются; всё недоказуемое остается нетронутым и репортится в лог. Ничего не удаляется наугад.

## Проверка, что runtime не подменили

```sh
printf 'x' | dd of=~/.sandboxes/…/runtime/bin/ctr bs=1 seek=5000 conv=notrunc   # any tampered bundle binary
rsbx run shell .
```

Ожидание:

```text
error: runtime artifact "ctr" … SHA-256 mismatch … refusing to launch an unverified artifact
```

Восстановите оригинальные байты (или перегенерируйте дайджесты), чтобы продолжить.

## Что пока не покрыто

Windows и native Linux хосты, rootless и вложенный Docker в гостях; провайдерские логины встроенных агентов; интерактивный OAuth удалённых MCP-серверов и OS-промпт согласований; L7 HTTPS interception; облачные команды. Всё это либо fail-closed, либо вне области альфы.
