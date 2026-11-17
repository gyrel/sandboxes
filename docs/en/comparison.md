# Docker `sbx` comparison

## Scope and method

This snapshot compares **Docker `sbx` v0.50.1** on macOS ARM64 (`/opt/homebrew/bin/sbx`, SHA-256 `a1e506d1b1f2e17bbc54a3b8e9850592860777689fe3f49098be6279b728c45e`) with **Rheic `rsbx` v0.0.54** (`rsbx-darwin-arm64`, SHA-256 `c3aad0a1fbfd3dc497cdaf1bfe55a659a629f9f34139be4a3bd5cb0421124841`). Both were queried on 17 November 2026 with `--help` for the top level and 27 matching commands; version and release checksums were checked separately. This is **CLI surface evidence**, not a same-input live behavior test. No sandbox was created or removed during this comparison.

| Scenario | Docker `sbx` v0.50.1 | Rheic `rsbx` v0.0.54 | Evidence status |
|---|---|---|---|
| Local `run [agent] [path]` | Creates or reuses and attaches; `--detach`, workspaces and `--` agent arguments | Same basic grammar and intent; local daemon required | Help compared; same-input runtime control pending |
| `create`, `exec`, `cp`, `ls`, `stop`, `rm`, `prune`, `ports` | Exposed | Exposed | Help compared; full side effects pending |
| `run` kit references | Local directory, ZIP, Git and OCI; mixins and kit arguments | Local kit file through `--kit`; no remote OCI or mixins | Confirmed CLI gap |
| Cloud `--cloud`, `move`, `ttl`, `volume` | Cloud paths exposed | No cloud backend; unsupported commands report an error | Confirmed product gap |
| `template` | List, inspect, save, load, remove | List and inspect built-in templates only | Confirmed CLI gap |
| `mcp` | Add, auth, inspect, load, list, remove, unload | List, add, call, remove | Confirmed CLI gap |
| `policy approval` | Approval commands exposed | Fails closed as unimplemented | Confirmed CLI gap |
| `secret` | Service and registry flows, including custom values | Import, list, set and remove; custom secret values unavailable | Confirmed CLI gap |
| `settings` | List, get, set, unset | Same command names; stores a validated local subset | Help compared; value and side-effect parity pending |
| Interactive TUI and agent sessions | Available | TUI command and preview agents exposed | Interactive parity pending |

**Do not infer parity from a shared command name.** Flags, prompts, exit codes, guest-visible state and cleanup need same-input live controls. The project [limits](limits.md) list runtime gates. `rsbx` is the Rheic binary; it does not occupy Docker's `sbx` name.

## Next controls

1. Use uniquely named sandboxes and synthetic credentials in isolated temporary state.
2. Run matching positive and negative scenarios on the same OS and architecture, recording flags, output, exit status, guest state and side effects.
3. Close each gap with code and contract tests, then update this table. Do not describe a row as parity until the controls pass.
