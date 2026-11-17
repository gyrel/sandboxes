# Безопасность и ограничения

Rheic — альфа-версия. Локальная VM использует containerd, patched nerdbox shim, libkrun, pinned guest kernel и rootfs, а также policy-enabled gateway. `rsbx` обращается к локальному daemon. Успех CLI-команды сам по себе не доказывает изоляцию гостя или применение policy.

| Область | Текущее evidence | Открытый пункт |
|---|---|---|
| macOS ARM64 VM | Локальные create/start/exec/stop и basic live guest boot зафиксированы | Полный Docker workload и network-policy parity |
| Linux ARM64 | Guest task запущен в собственной nested KVM Lima VM | Native Linux host и rootless qualification |
| Native bundle | Точный file inventory, archive checksums, basic VM boot | Независимая provenance native-архивов; macOS notarization |
| Windows WHP | Реализации нет | Сборка и живой runtime |
| Cloud | Rheic cloud backend отсутствует | Docker `--cloud`, `move`, `ttl`, `volume` |
| Security review | Внутренние tests и CI есть | Независимый внешний review не выполнен |

CLI по умолчанию использует network profile `allow-all`. При необходимости выберите более узкий профиль и проверьте фактическую конфигурацию gateway. Help и state-only daemon не доказывают enforcement сети. Direct workspace даёт гостю доступ к host-файлам; `--clone` использует приватную копию. Secrets и host hooks требуют явного доверия и ограниченного окружения.

Подробный evidence ledger и продуктовые gates ведутся во внутреннем PLAN. Сводка CLI — в [сравнении](comparison.md). На публичном сайте наблюдаемые результаты отделены от открытых пунктов.
