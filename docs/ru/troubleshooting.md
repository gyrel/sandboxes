# Решение проблем

Начните с версии установленного бинарника и его встроенной справки:

```sh
rsbx --help
rsbx diagnose
sandboxesd --help
```

`rsbx diagnose` печатает секционный отчёт (installation, platform, storage, connection) из отдельно оценённых проверок со сводкой pass/fail/warning/skip и завершается с ненулевым кодом при падении проверки. `--json` выводит плоский отчёт sbx (`version`, `checks[]`, `summary`), а `--format github-issue` создаёт Markdown-текст issue. `rsbx policy log` показывает записанные в каталоге run daemon решения gateway audit (allowed/denied destinations с сработавшим правилом).

## CLI не подключается

Укажите CLI тот же локальный socket, который использует daemon:

```sh
rsbx --socket "$HOME/.sandboxes/sandboxesd.sock" ls
```

Проверьте, что daemon запущен и текущий пользователь имеет доступ к socket. Переменная `SANDBOXES_SOCKET` задаёт путь по умолчанию. Используйте `rsbx daemon status`, чтобы проверить live endpoint, версию, версию API и путь логов. Не заменяйте неизвестный socket или каталог состояния.

## Daemon не останавливается

`rsbx daemon stop` сигналит только тому daemon, чью идентичность удалось доказать. Daemon, запущенный вне `rsbx daemon start`, останавливается, если его идентичность доказана по live socket peer. Если доказать её нельзя, stop отказывается сигналить и печатает actionable-сообщение. Проверьте процесс, владеющий socket, остановите его вручную через `SIGTERM` и проверьте endpoint перед удалением состояния. На платформах, где определить socket peer невозможно, команда решает по control record. Устаревшие socket и control records нужно проверять, а не удалять вслепую.

## Sandbox не запускается

Резервный режим state-only из [быстрого старта](quickstart.md) поднимает control plane, но не настраивает VM backend, поэтому сама по себе эта команда VM не запускает. Для гостевого выполнения нужны совместимые containerd, runtime, guest image, shim и вспомогательные артефакты, настроенные по документации конкретной платформы. VM-backed CLI lifecycle и exec-проверки прошли live acceptance на macOS ARM64; это не подтверждает полный агентский workflow. Windows WHP не реализован, Linux KVM не квалифицирован. Сверьте платформу и режим запуска с [требованиями](requirements.md) и [архитектурой](architecture.md). `rsbx start` завершается fail-closed, если у daemon нет runtime backend, и возвращает sandbox в состояние stopped.

## Не работает сеть

Новые sandboxes по умолчанию используют профиль egress `allow-all`. Если sandbox создан с `deny-all` или сработало явное deny-правило, проверьте политику sandbox, настроенный gateway и DNS upstream. Добавляйте только необходимые правила назначения. `rsbx policy check` проверяет сохранённые входные данные политики, но не подтверждает реальное применение фильтра gateway. `rsbx policy log` печатает последние решения gateway audit с сработавшим правилом; `rsbx policy inspect RULE_ID|SANDBOX` показывает детали одного правила или политики sandbox. См. [Сеть и порты](networking.md).

## Вход в Docker прошёл, но guest не скачивает образы

Авторизация аккаунта Docker хранится на хосте. Передача credentials реестра в guest экспериментальна и ещё не прошла live-приёмку в VM. См. [Docker](docker.md).

## Имя уже связано с другой workspace

Для другой workspace укажите новое имя sandbox или проверьте существующую через `rsbx get NAME`. Не рассчитывайте, что повторное имя переключит подключённый каталог хоста.

## После удаления sandbox файлы хоста остались

Удаление sandbox не удаляет host workspace. Сначала проверьте её расположение, затем удаляйте файлы самостоятельно: Gyrel не владеет произвольными каталогами хоста.

Если проблему не удалось решить, проверьте вывод `rsbx diagnose` на локальные пути и чувствительные метаданные и приложите точные версии модулей и платформу. Не прикладывайте credentials или неотредактированные secrets.
