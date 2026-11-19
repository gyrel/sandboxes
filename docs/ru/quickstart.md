# Начало работы

Здесь проверяется **выпущенный локальный control plane** на macOS ARM64. Для VM нужны отдельно настроенные native runtime-процессы и assets; один CLI installer VM не запускает.

## Установить CLI и daemon

Установите `rsbx` v0.0.64 через [CLI installer](https://github.com/rheic/sandboxes-cli/blob/main/scripts/install.sh) или скачайте платформенный asset из [CLI release](https://github.com/rheic/sandboxes-cli/releases/tag/v0.0.64). Перед установкой проверьте `SHA256SUMS` и attestation CLI. Скачайте `sandboxesd` v0.0.74 из [daemon release](https://github.com/rheic/sandboxes-daemon/releases/tag/v0.0.74) и также проверьте checksum и attestation. Держите оба бинаря в своём `PATH`; не заменяйте Docker `sbx`.

```sh
rsbx version
sandboxesd --version
```

## Проверить локальный control plane

Используйте отдельный приватный state-каталог и socket. Запуск без `--containerd` — **state-only**: daemon отвечает CLI, но не запускает гостя.

```sh
mkdir -p "$HOME/.sandboxes"
sandboxesd --state "$HOME/.sandboxes" --socket "$HOME/.sandboxes/sandboxesd.sock"
```

В другом терминале:

```sh
rsbx ls --json
rsbx diagnose
```

После проверки остановите запущенный вами процесс. Эти команды не создают sandbox. `rsbx daemon stop` сигналит только daemon с доказанной идентичностью; процесс, запущенный вручную, может потребоваться остановить в исходном терминале.

## Запустить VM

Для VM нужны совместимый containerd, patched nerdbox shim, libkrun, kernel, EROFS rootfs, `gvproxy` для сети и filesystem tools. [Runtime v0.0.36](runtime.md) публикует ARM64 assets с точным inventory; код runtime v0.0.41 использует те же native assets. Выпущенная пара CLI v0.0.64 / daemon v0.0.74 и эти assets квалифицированы для read-only shared skills на macOS ARM64 и Linux/KVM ARM64. **Другие workload и полная Docker parity не квалифицированы.** Для изолированной VM-проверки следуйте runtime build и настройке daemon; state-only проверка не доказывает VM boot.

После настройки VM backend `rsbx run shell .` создаёт или повторно использует локальный sandbox, запускает его и подключается к гостю. Текущий каталог монтируется по умолчанию; выберите отдельный проект или `--clone` для гостевой копии. См. [CLI](cli.md) и [ограничения](limits.md).
