# Docker `sbx` comparison

This page records which parts of the Docker `sbx` and Gyrel `rsbx` CLI surface have a recorded control, and which remain `unverified`.

## Scope and method

The comparison covers Docker `sbx` v0.50.1 and Gyrel `rsbx` CLI 0.0.81 on macOS ARM64. The pinned binaries carry SHA-256 `a1e506d1b1f2e17bbc54a3b8e9850592860777689fe3f49098be6279b728c45e` for sbx and `085ec502869ff6c86efacca84af8078a20bd1367f929af496ce007578a1b8669` for rsbx. The release record pairs this CLI with daemon 0.0.104 and API contract 0.0.38. The probe exercised the CLI binary only.

Controls were captured on 2026-11-27 on macOS ARM64. Both binaries were run with `--help` at the top level and per command. The probe also ran `version`, `--version` and argument-validation error paths. No sandbox was created, no daemon was started, and no authenticated flow was run. Surface evidence does not establish runtime parity.

## Status vocabulary

| Status | Meaning |
|---|---|
| `parity` | Same input on both binaries produced the same recorded result. No row uses this status in this probe. |
| `partial` | Some surface behaviours are recorded; the row lists the gaps. |
| `differs` | Recorded, intentional divergence; the row states the rationale. |
| `gap` | Not implemented; accepted alpha limitation. |
| `unverified` | Implemented or present, but no recorded control. |

## Comparison

| Slug | Area | sbx v0.50.1 | rsbx (CLI 0.0.81 / daemon 0.0.104) | Status | Evidence still required | Closed by |
|---|---|---|---|---|---|---|
| `run` | run | Top-level and `run` help compared. Cloud flags include `--detach-keys` on `run`, `--ttl` and `--volume`. | Local grammar. `--detach-keys` is absent from `run`; `--template` aliases `--image`; `--kit` takes one string. | unverified | E1 same-input run control over create, attach and exec; E3 for malformed inputs | — |
| `create` | create | Full flag set, including cloud `--image-ref`, `--profile`, `--mount`, `--ttl` and `--volume`. | `--image` replaces `--image-ref`; `--policy-profile` replaces `--profile`; `--kit` is single; `--skills readwrite` is unsupported; `--deny-write`, `--docker` and `--idempotency-key` are added. | partial | E2 atomicity under kill; E3 for `NAME_INVALID` and `AUDIT_CAP_EXCEEDED`; E1 grammar corpus | CR-1…CR-5 |
| `exec` | exec | Full flag set, including `--privileged` and `--detach-keys`. | Flag set is identical. `--privileged` is rejected by the local runtime; `--detach-keys` is cloud-only. | partial | E3 for 125, 126 and 127, and for `APPROVAL_PROVIDER_UNAVAILABLE`; E1 exit-code fixture; live PTY stays `gap` | EX-1…EX-6 |
| `cp` | cp | `-L/--follow-link` follows symlinks and refuses out-of-workspace escapes. | `-L/--follow-link` follows a top-level source symlink; nested links are rejected. | partial | E3 for `MEMBER_TYPE_REFUSED`, `LINK_ESCAPE` and `HOST_PATH_NOT_ALLOWED`; E2 tree-hash rollback | CP-1…CP-6 |
| `ls` | ls | `--format`, `--json` and `-q/--quiet`. | Same flags; adds `--limit` (1–1000). | partial | E2 JSON schema fixture; E3 for daemon-down `unknown`; masking byte-grep | LS-1…LS-4 |
| `stop` | stop | `--format` and `--json`. | Same flags; adds `--grace`. | unverified | E1 stop/start cycle; E3 for `NOT_OWNED` and `SESSION_UNREAPED`; E2 port release | SR-1…SR-6 |
| `rm` | rm | `--all`, `-f/--force`, `--format` and `--json`. | Same flags. Without `--force`, every named sandbox must be stopped or nothing is removed. | unverified | E3 per-item refusal; E2 tree diff proving one deletion; E1 idempotent re-rm | SR-1, SR-2, SR-5 |
| `prune` | prune | `--filter stringArray` (repeatable), `--dry-run`, `-f/--force`, `--format` and `--json`; secrets scoped to pruned sandboxes are deleted. | `--filter string` (single); `until=TIMESTAMP` or `until=DURATION`; same remaining flags; secret cleanup is not documented. | unverified | E3 for the four `UNCLASSIFIED` classes; E2 whole-tree hash on abort; E1 dry-run and real plan diff | PR-1…PR-8 |
| `ports` | ports | `[[HOST_IP:]HOST_PORT:]SANDBOX_PORT[/PROTOCOL]`; documented tcp4 default, dual-stack loopback and cloud binding rules. | `[[HOST_IP:]HOST_PORT:]GUEST[/tcp\|udp\|tcp4\|udp4\|tcp6\|udp6]`; default-protocol and loopback-family rules are not documented; no cloud section. | partial | E1 over 6 canonical and 10 malformed specs; E2 lease table fixture; E3 for `PORT_IN_USE`, `PORT_RESERVED`, `BIND_FORBIDDEN` and `POLICY_DENY` | PT-1…PT-6 |
| `kits` | kits | `--kit strings` (repeatable); local directory, ZIP, Git and OCI; mixins and kit arguments. | `--kit string` (single local kit); no remote OCI or mixins. | unverified | E1 kit lifecycle corpus | — |
| `cloud` | cloud backend | `--cloud`, `move`, `ttl` and `volume`. | No `--cloud`. `move`, `ttl` and `volume` are registered but return `unsupported` with exit 1. | gap | None. Accepted alpha limitation, listed in [limits](limits.md). | non-goal |
| `template` | templates | `inspect`, `load`, `ls`, `rm` and `save`. | Same subcommands plus `export`. | partial | E4 entry for the P1.5 roundtrip; E1 whiteout edge cases | — |
| `mcp` | MCP | `add`, `auth`, `inspect`, `load`, `ls`, `rm` and `unload`. | Same subcommands plus `call`. | partial | E1 add, list, call and remove; E3 for the literal-header gap | non-goal for the header gap |
| `policy-approval` | policy approval | `policy approval` is listed with `inspect`, `ls` and `respond`. | `policy approval` is retained but hidden; `policy org` is the documented surface. The `inspect`, `ls` and `respond` shapes match. | differs | E3 fail-closed refusal code; E1 challenge path | EX-2 |
| `secret` | secrets | `import`, `ls`, `rm`, `set` and `set-custom`; alias `secrets`. | Same subcommands and alias. | partial | E3 command-source rejection; X-3 redaction over vault paths and `ls` output | LS-3, X-3 |
| `settings` | settings | `get`, `ls`, `set` and `unset`. | Same subcommands; documents `~/.config/rheic/settings.toml` and the sbx settings record shape. | partial | E1 over the full sbx settings name list; E3 for `SETTINGS_INVALID` | X-5 |
| `tui` | TUI | `tui` command. | `tui` command present in top-level help. | unverified | Scripted-terminal E1 equivalent (keystroke log and frame dump); LS-4 | LS-4 |
| `login-logout` | login/logout | `login` and `logout` under Other. | `login` and `logout` under Management. | unverified | E4 entry for a same-input login/logout control; E3 for the account-name gap | — |
| `help-layout` | help layout | Cobra sections: Sandbox, Management, Experimental, Other. Unknown command with `--help` prints the nearest ancestor help and exits 0. | Sections add Unsupported Docker Sandboxes Commands. `template` moves to Experimental; `env`, `login` and `logout` move to Management; `agents` is rsbx-only. Unknown command with `--help` exits 1. | differs | E4 entry with both SHAs and a diff artifact for any parity claim | — |
| `policy-ls` | policy ls | `policy ls` reports default allow rules in a `POLICY / SOURCE / APPLIES TO / SUMMARY` table. | `policy ls` is present; baseline rules output was not captured. | unverified | E4 entry with a committed baseline fixture | — |

Two rows are `differs` on recorded surface evidence. `policy-approval` keeps `policy approval` as a hidden retained command and documents `policy org` instead. `help-layout` uses strict unknown-command handling, so an unknown command with `--help` exits 1 instead of printing ancestor help.

## Side-effect protection

The former combined `create`–`ports` row is split by slug. The probe compared flag and subcommand grammar, version output and argument-validation error paths. It did not exercise sandbox creation, guest state, cleanup, port leases or policy enforcement.

Side-effect protection is in progress: the B0/B1 guards are landing. No control in this probe exercises them. Controls will be recorded per E4 before a row moves beyond `partial`.

**Do not infer parity from a shared command name.** A matching command or flag name is not evidence of matching behaviour. Flags, prompts, exit codes, guest-visible state and cleanup need same-input live controls. Runtime gates are listed in [limits](limits.md). `rsbx` is the Gyrel binary; it does not occupy Docker's `sbx` name.

## Evidence and limits

All controls were recorded on 2026-11-27. Raw captures are in `/tmp/rheic-gyrel-20261127/probe-logs/`. The manifest is `/tmp/rheic-gyrel-20261127/EXECUTOR-REPORT-PROBE.md`. Artifact paths below are relative to the capture directory.

### E1 — same-input surface captures

| Control | Scope | Artifact |
|---|---|---|
| Control 1 | `version` and `--version` on both binaries, with SHA-256 | `00-control1-version-sha.txt` |
| Control 2 | Top-level `--help` section inventory | `01-sbx-help.txt`, `02-rsbx-help.txt` |
| Control 3 | Per-flag comparison for 8 verbs | `sbx-*-help.txt`, `rsbx-*-help.txt` |
| Control 4 | Management verbs: template, mcp, policy, secret, settings, agents | `sbx-{template,mcp,policy,secret,settings}-help.txt`, `rsbx-{template,mcp,policy,secret,settings,agents}-help.txt` |
| Control 5 | `prune --help` grammar | `sbx-prune-help.txt`, `rsbx-prune-help.txt` |
| Control 6 | `ports` grammar | `sbx-ports-help.txt`, `rsbx-ports-help.txt` |
| Control 7 | `run --detach` and detach keys | `sbx-run-detach-help.txt`, `rsbx-run-detach-help.txt` |

### E3 — negative controls

| Control | Scope | Artifact |
|---|---|---|
| Control 8 | Unknown commands, documented aliases, unsupported commands | `09-exit-codes.txt` |
| Control 9 | Exit-code matrix for missing arguments, unknown flags and unknown commands | `09-exit-codes.txt` |

### E2 — state assertions

None recorded. The probe made no filesystem or guest-state changes.

### E4 — ledger entries

None recorded yet. This section is the manifest the ledger will be seeded from. Each entry needs a control id, date, runner identity, both component versions and SHAs, the command pair, and the artifact path.

### Pending controls

The following controls do not exist yet. Rows that need them for a stronger status stay `partial` or `unverified`.

- E2 state assertions: `create` atomicity, `cp` rollback, `ls` JSON schema, `stop` port release, `rm` tree diff, `prune` abort hash, `ports` lease table.
- E3 per-verb refusal codes: `create` `NAME_INVALID` and `AUDIT_CAP_EXCEEDED`; `exec` 125, 126, 127 and `APPROVAL_PROVIDER_UNAVAILABLE`; `cp` `MEMBER_TYPE_REFUSED`, `LINK_ESCAPE` and `HOST_PATH_NOT_ALLOWED`; `stop` `NOT_OWNED` and `SESSION_UNREAPED`; `ports` `PORT_IN_USE`, `PORT_RESERVED`, `BIND_FORBIDDEN` and `POLICY_DENY`; `secret` command-source rejection; `settings` `SETTINGS_INVALID`.
- E1 runtime controls: `run` create, attach and exec cycle; `kits` lifecycle; `tui` scripted-terminal capture; `login` and `logout` same-input run; `policy ls` fixture; `policy-approval` challenge path; `help-layout` diff artifact.

Rows that depend on these missing controls and stay `unverified`: `run`, `stop`, `rm`, `prune`, `kits`, `tui`, `login-logout`, `policy-ls`. The `partial` rows list their gaps in place and claim no parity. `policy-approval` and `help-layout` are `differs` on the recorded surface difference. Their runtime behaviour remains unverified.

Agent sessions and authenticated Codex controls are outside this probe. See [agents](agents.md) and [limits](limits.md) for current limits.
