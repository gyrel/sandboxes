# Docker `sbx` comparison

## Scope and method

This snapshot compares **Docker `sbx` v0.50.1** on macOS ARM64 (`/opt/homebrew/bin/sbx`, SHA-256 `a1e506d1b1f2e17bbc54a3b8e9850592860777689fe3f49098be6279b728c45e`) with **Rheic `rsbx` v0.0.58** (`rsbx-darwin-arm64`, SHA-256 `eb05f27aac36fa212a436689a7961390bba369ea61f03c928586194a1562f1ec`). Both were queried on 17 November 2026 with `--help` for the top level and 27 matching commands; version and release checksums were checked separately. This is **CLI surface evidence**, not a same-input live behavior test. No sandbox was created or removed during this comparison.

| Scenario | Docker `sbx` v0.50.1 | Rheic `rsbx` v0.0.58 | Evidence status |
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
| `login` / `logout` | Device code, browser sign-in, `Signed in as <user>.`; a second login reports the existing session | Same device flow, prompt text, hints and exit codes after the v0.0.55 fix; the account name is not shown yet | Live comparison and released-binary controls passed |
| Command surface | `start`, `get` and `wait` are unknown commands; `ls`/`rm`/`secret` have documented aliases | Same: the extra commands were removed in v0.0.57 and the aliases restored | Live comparison passed |
| `--help` layout | Cobra sections with a full flag table | Same section layout for every command, listing only implemented flags | Rendered and compared |
| `policy ls` | Reports default allow rules in a `POLICY / SOURCE / APPLIES TO / SUMMARY` table | Same baseline rules for `allow-all` and the same table; the per-sandbox kit policy row is absent | JSON compared field by field for the baseline rules |

**Do not infer parity from a shared command name.** Flags, prompts, exit codes, guest-visible state and cleanup need same-input live controls. The project [limits](limits.md) list runtime gates. `rsbx` is the Rheic binary; it does not occupy Docker's `sbx` name.

## Live Codex check: signed-out controls

On 17 November 2026, both binaries were run on macOS ARM64 with fresh private state, an empty workspace, a unique sandbox name and no user credentials. `sbx run --detach codex` and `sbx create codex` both exited 1 before sandbox creation with `not signed in to Docker`. Rheic `rsbx run --detach codex` exited 1 after OpenAI OAuth returned no credentials. Rheic `rsbx create codex` reached the pinned Codex template image, then Docker Hub returned `401 Unauthorized` to the anonymous manifest request. The exact owned names were absent afterward; temporary daemon and containerd processes were stopped.

This is a **negative live comparison**, not a completed Codex session. The products have different prerequisite and error order. A successful same-input guest task remains unverified because Docker sign-in and access to the pinned image require authenticated credentials; the probe did not use real user credentials.

## Next controls

1. Use uniquely named sandboxes and synthetic credentials in isolated temporary state.
2. Run matching positive and negative scenarios on the same OS and architecture, recording flags, output, exit status, guest state and side effects.
3. Close each gap with code and contract tests, then update this table. Do not describe a row as parity until the controls pass.

## Authenticated Codex run: confirmed gap

With the account owner's approval, the same empty workspace and the same prompt were tested on macOS ARM64 on 17 November 2026. Docker `sbx v0.50.1` started its Codex guest, reported `codex-cli 0.165.0`, and `codex exec --skip-git-repo-check` returned `RHEIC_CODEX_PARITY_OK` with exit 0. Rheic `rsbx v0.0.54`, using a locally built daemon from the `v0.0.62` source plus an unmerged Keychain size fix and the released native runtime `v0.0.36`, started the same image and reported the same Codex version. Its OpenAI browser login and token exchange completed, but Codex reported `Not logged in`; the same prompt received HTTP `401 Unauthorized` from the OpenAI Responses endpoint. An explicit OAuth proxy reference on `rsbx exec` produced the same 401. This is a **confirmed authentication gap**, not Codex parity. The Keychain size fix that run depended on shipped in CLI v0.0.56 and daemon v0.0.63, but the Codex guest authentication path has not been re-tested on the v0.0.58 pair, so the gap stays open.

The initial Rheic test also returned DNS `REFUSED` because the isolated daemon had no DNS upstream while egress policy was enabled. Restarting that owned sandbox with `-dns-upstream 1.1.1.1:53` restored DNS and exposed the independent 401. The released daemon initially could not start a proxy route without a separately built guest proxy helper. The Keychain fix successfully stored the large OpenAI token record in the host vault, but it has not been merged or released. No token values were recorded. Both uniquely named test sandboxes were removed; unrelated Docker sandboxes were untouched. Completed authenticated Codex tasks in Rheic remain a release blocker.
