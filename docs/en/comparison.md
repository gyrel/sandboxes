# Docker `sbx` comparison

The page pairs Docker `sbx` v0.50.1 with Gyrel `rsbx` 0.0.81 command by command. Each row
states what a recorded control shows, and the page names the controls still required
before a row can move to a stronger status.

## Scope

| Item | Value |
|---|---|
| Baseline binary | Docker `sbx` v0.50.1, SHA-256 `a1e506d1b1f2e17bbc54a3b8e9850592860777689fe3f49098be6279b728c45e` |
| Product binary | Gyrel `rsbx` CLI 0.0.81, SHA-256 `085ec502869ff6c86efacca84af8078a20bd1367f929af496ce007578a1b8669` |
| Release record pairing | daemon 0.0.104, API contract 0.0.38 |
| Platform | macOS ARM64 |
| Capture date | 2026-11-27 |
| Method | top-level `--help`, per-command `--help`, `version`, `--version` and argument-validation error paths |
| Not exercised | sandbox creation, daemon start, authenticated flows, guest state, port leases and policy enforcement |

The probe ran both binaries with `--help` at the top level and per command, plus `version`,
`--version` and argument-validation error paths. It created no sandbox, started no daemon
and ran no authenticated flow. Surface evidence does not establish runtime parity.

## Status vocabulary

| Status | Meaning |
|---|---|
| `parity` | Same input produced the same recorded result on both binaries under a live control. |
| `partial` | Some surface behaviours are recorded; the missing ones are named per row. |
| `differs` | Recorded intentional divergence; the rationale is stated on this page. |
| `gap` | Not implemented; accepted alpha limitation, tracked in [limits](limits.md). |
| `unverified` | Implemented or present, with no recorded same-input control yet. |

No row carries `parity` yet.

## Command surface

| Command | Docker `sbx` v0.50.1 | Gyrel `rsbx` 0.0.81 | Status |
|---|---|---|---|
| `run` | Top-level and `run` help compared. Cloud flags include `--detach-keys` on `run`, `--ttl` and `--volume`. | Local grammar. `--detach-keys` is absent from `run`; `--template` aliases `--image`; `--kit` takes one string. | `unverified` |
| `create` | Full flag set, including cloud `--image-ref`, `--profile`, `--mount`, `--ttl` and `--volume`. | `--image` replaces `--image-ref`; `--policy-profile` replaces `--profile`; `--kit` is single; `--skills readwrite` is unsupported; `--deny-write`, `--docker` and `--idempotency-key` are added. | `partial` |
| `exec` | Full flag set, including `--privileged` and `--detach-keys`. | Flag set is identical. `--privileged` is rejected by the local runtime; `--detach-keys` is cloud-only. | `partial` |
| `cp` | `-L/--follow-link` follows symlinks and refuses out-of-workspace escapes. | `-L/--follow-link` follows a top-level source symlink; nested links are rejected. | `partial` |
| `ls` | `--format`, `--json` and `-q/--quiet`. | Same flags; adds `--limit` (1–1000). | `partial` |
| `stop` | `--format` and `--json`. | Same flags; adds `--grace`. | `unverified` |
| `rm` | `--all`, `-f/--force`, `--format` and `--json`. | Same flags. Without `--force`, every named sandbox must be stopped or nothing is removed. | `unverified` |
| `prune` | `--filter stringArray` (repeatable), `--dry-run`, `-f/--force`, `--format` and `--json`; secrets scoped to pruned sandboxes are deleted. | `--filter string` (single); `until=TIMESTAMP` or `until=DURATION`; same remaining flags; secret cleanup is not documented. | `unverified` |
| `ports` | `[[HOST_IP:]HOST_PORT:]SANDBOX_PORT[/PROTOCOL]`; documented tcp4 default, dual-stack loopback and cloud binding rules. | `[[HOST_IP:]HOST_PORT:]GUEST` with protocol suffix `/tcp`, `/udp`, `/tcp4`, `/udp4`, `/tcp6` or `/udp6`; default-protocol and loopback-family rules are not documented; no cloud section. | `partial` |
| `kits` | `--kit strings` (repeatable); local directory, ZIP, Git and OCI; mixins and kit arguments. | `--kit string` (single local kit); no remote OCI or mixins. | `unverified` |
| `--cloud` | `--cloud`, `move`, `ttl` and `volume`. | No `--cloud`. `move`, `ttl` and `volume` are registered but return `unsupported` with exit 1. | `gap` |
| `template` | `inspect`, `load`, `ls`, `rm` and `save`. | Same subcommands plus `export`. | `partial` |
| `mcp` | `add`, `auth`, `inspect`, `load`, `ls`, `rm` and `unload`. | Same subcommands plus `call`. | `partial` |
| `policy approval` | `policy approval` is listed with `inspect`, `ls` and `respond`. | `policy approval` is retained but hidden; `policy org` is the documented surface. The `inspect`, `ls` and `respond` shapes match. | `differs` |
| `secret` | `import`, `ls`, `rm`, `set` and `set-custom`; alias `secrets`. | Same subcommands and alias. | `partial` |
| `settings` | `get`, `ls`, `set` and `unset`. | Same subcommands; documents `~/.config/rheic/settings.toml` and the sbx settings record shape. | `partial` |
| `tui` | `tui` command. | `tui` command present in top-level help. | `unverified` |
| `login` and `logout` | `login` and `logout` under Other. | `login` and `logout` under Management. | `unverified` |
| help layout | Cobra sections: Sandbox, Management, Experimental, Other. Unknown command with `--help` prints the nearest ancestor help and exits 0. | Sections add Unsupported Docker Sandboxes Commands. `template` moves to Experimental; `env`, `login` and `logout` move to Management; `agents` is rsbx-only. Unknown command with `--help` exits 1. | `differs` |
| `policy ls` | `policy ls` reports default allow rules in a `POLICY / SOURCE / APPLIES TO / SUMMARY` table. | `policy ls` is present; baseline rules output was not captured. | `unverified` |

!!! info "Command names are not evidence"

    A matching command or flag name is not evidence of matching behaviour. Flags, prompts,
    exit codes, guest-visible state and cleanup need same-input live controls. `rsbx` is
    the Gyrel binary; it does not occupy Docker's `sbx` name. Runtime boundaries are
    listed in [limits](limits.md).

## Controls still required

The probe exercised the CLI surface only. Side-effect guards for `create`, `cp` and `ports`
are in implementation; no recorded control on this page exercises them yet. A row moves to
a stronger status only after its controls are recorded in the ledger
`docs/controls/ledger.jsonl`.

| Command | Controls required |
|---|---|
| `run` | Same-input control over the create, attach and exec cycle; negative controls for malformed inputs. |
| `create` | State assertion for atomicity under kill; negative controls for `NAME_INVALID` and `AUDIT_CAP_EXCEEDED`; same-input grammar control over the full flag corpus. |
| `exec` | Negative controls for exit codes 125, 126 and 127 and for `APPROVAL_PROVIDER_UNAVAILABLE`; same-input exit-code fixture; live PTY remains a gap. |
| `cp` | Negative controls for `MEMBER_TYPE_REFUSED`, `LINK_ESCAPE` and `HOST_PATH_NOT_ALLOWED`; state assertion for tree-hash rollback. |
| `ls` | State assertion for the JSON schema; negative control for the `unknown` state when the daemon is down; masking byte-grep control. |
| `stop` | Same-input stop/start cycle; negative controls for `NOT_OWNED` and `SESSION_UNREAPED`; state assertion for port release. |
| `rm` | Negative control for per-item refusal; state assertion by tree diff over one deletion; same-input idempotent re-remove control. |
| `prune` | Negative controls for the four `UNCLASSIFIED` classes; state assertion for the whole-tree hash on abort; same-input dry-run and real-run plan diff. |
| `ports` | Same-input control over 6 canonical and 10 malformed specs; state assertion for the lease table; negative controls for `PORT_IN_USE`, `PORT_RESERVED`, `BIND_FORBIDDEN` and `POLICY_DENY`. |
| `kits` | Same-input control over the kit lifecycle corpus. |
| `template` | Ledger entry for the recorded template roundtrip; same-input control over whiteout edge cases. |
| `mcp` | Same-input control over add, list, call and remove; negative control for the literal-header gap. |
| `policy approval` | Negative control for the fail-closed refusal code; same-input control over the challenge path. |
| `secret` | Negative control for command-source rejection; redaction control over vault paths and `ls` output. |
| `settings` | Same-input control over the full `sbx` settings name list; negative control for `SETTINGS_INVALID`. |
| `tui` | Scripted-terminal equivalent of a same-input control: keystroke log and frame dump. |
| `login` and `logout` | Ledger entry pairing a same-input login/logout control; negative control for the account-name gap. |
| help layout | Ledger entry with both binary SHAs and a diff artifact before any parity claim. |
| `policy ls` | Ledger entry with a committed baseline fixture. |

## Intentional differences

| Area | What differs | Basis |
|---|---|---|
| `policy approval` | The command is retained but hidden; `inspect`, `ls` and `respond` match the `sbx` shapes. | The documented approval surface is `policy org`. |
| help layout | An unknown command with `--help` exits 1 instead of printing ancestor help; `template` moves to Experimental, `env`, `login` and `logout` move to Management; an Unsupported section is added; `agents` is rsbx-only. | Strict unknown-command handling, recorded as intentional. |
| `--cloud` | `--cloud` is absent; `move`, `ttl` and `volume` return `unsupported` with exit 1. | Accepted alpha non-goal, tracked in [limits](limits.md). |
| `mcp` header | Recorded gap in literal header handling. | Non-goal for the current release. |

## Evidence and limits

All statuses reflect controls captured on 2026-11-27. The recorded controls below resolve
against the machine-readable ledger `docs/controls/ledger.jsonl`, which carries each
artifact path and digest.

### Recorded controls

| Control | Scope |
|---|---|
| `E1-01` | `version` and `--version` on both binaries, with SHA-256. |
| `E1-02` | Top-level `--help` section inventory. |
| `E1-03` | Per-flag grammar comparison for 8 verbs. |
| `E1-04` | Management verbs: template, mcp, policy, secret, settings, agents. |
| `E1-05` | `prune --help` grammar. |
| `E1-06` | `ports` grammar. |
| `E1-07` | `run --detach` and detach keys. |
| `E3-08` | Unknown commands, documented aliases, unsupported commands. |
| `E3-09` | Exit-code matrix for missing arguments, unknown flags and unknown commands. |

### Pending records

Entries for the current `sbx`/`rsbx` pair that do not exist yet stay `pending` in the
ledger and are not cited as evidence. The ledger also carries historical state assertions
from earlier rounds; they do not close current-pair rows. Agent sessions and authenticated
Codex controls are outside this probe; see [agents](agents.md) and [limits](limits.md).
