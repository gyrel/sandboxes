# CLI reference

The canonical user-facing executable is `rsbx`. The current release line is CLI `rsbx` v0.0.85 with daemon `sandboxesd` v0.0.108, local API contract 0.0.38, SDK 0.0.36, and runtime v0.1.2. Most commands accept `--socket PATH`; `SANDBOXES_SOCKET` can set the same default for a shell session.

> **Alpha note:** this page documents the published CLI interface. Runtime and daemon include exec/PTY paths, and the VM-backed lifecycle passed live acceptance on macOS ARM64. Full interactive agent workflows, Windows WHP, cloud commands, and platform parity remain out of scope or unverified. No independent external security review has been completed. See [requirements](requirements.md) before configuring a VM backend.

## Create and run

```sh
rsbx run shell .
rsbx run --detach --name api --cpus 2 --memory 2g shell .
rsbx create --name api shell . /path/to/docs:ro
rsbx run --clone shell .
```

`--clone` mounts the single workspace read-only and works in a private in-guest clone, exposing agent commits through the host remote `sandbox-<name>` while the sandbox runs. The remote URL contains a random per-sandbox token: `git://127.0.0.1:<port>/<token>/<repository>`. The image must provide `git` and `git daemon`, and an existing non-empty destination is rejected. See [workspaces and files](workspaces.md#clone-mode) for the lifecycle, endpoint form, and limits.

The CLI grammar defines `run` as create-or-reuse, start, and attach. Runtime and daemon include exec/PTY implementations, and VM-backed lifecycle checks passed on macOS ARM64. The complete agent lifecycle has not passed shared platform acceptance. The current directory is the default workspace. `--detach` returns after startup; `create` creates without attaching. `rsbx agents list` shows the built-in agent registry, image, launch command, and authentication notes.

## Inspect and control

```sh
rsbx ls
rsbx get api
rsbx start api
rsbx stop api
rsbx exec -it api /bin/sh
rsbx rm --force api
```

`ls` lists sandboxes; `get` shows a sandbox's details; `ports` reports published ports. `start`, `stop`, and `rm` accept multiple sandbox names. `rm` refuses to remove a running sandbox unless `--force` is supplied. `rm --all` removes every sandbox, so inspect the list first. `rsbx stop` stops a sandbox; it is separate from `rsbx daemon stop`, which manages the daemon process.

## Machine-readable output {#machine-readable-output}

`ls`, `rm`, `stop`, `prune`, `secret ls`, `policy ls`, `policy check`, `settings`, and `diagnose` accept `--format table|json|yaml`, and most also accept `--json` as a shorthand for JSON. `--json` cannot be combined with an explicit `--format`. Table output remains the default and is unchanged by the sbx-compatible schemas.

- `ls --json` emits an array of `name`, `id`, `agent`, `status`, `last_used_at`, `workspaces`, and `created_at` records. `get --json` emits one record with the same fields; `get` is a Gyrel extension.
- `rm --json` and `stop --json` emit an array of `{action, resource, name}` records. `start` still emits operation records rather than the sbx mutation shape.
- `prune --dry-run --json` emits `{"would_remove":[...],"skipped_unknown_stop":[...]}`; an actual prune removal uses the same `{action, resource, name}` records as `rm`.
- `secret ls --json` uses the sbx secret inventory envelope and never includes a secret value.
- `policy ls --json` emits `{"rules":[...]}` with `id`, `name`, `policy_id`, `scope`, `applies_to`, `resource_type`, `decision`, `resources`, `origin`, `layer`, `status`, `editable`, `provenance`, `actions`, and `sandbox_id` for scoped rules. `policy check network --json` emits the sbx verdict fields.
- `settings ls --json` and `settings get --json` emit typed records: `key`, `value`, `type`, `source`, `default`, `env_var` where defined, and `requires_restart` when needed.
- `diagnose --json` emits the flat sbx report: `version`, `checks[]` with `name`, `status`, `message`, `detail`, `hint`, and a `summary`. `--format github-issue` produces a Markdown issue body with the JSON report embedded.

Empty result sets for `ls`, `rm`, `stop`, and `prune` are emitted as `[]` where the sbx schema expects an array.

## Workspaces and files

```sh
rsbx run shell . /path/to/reference:ro
rsbx cp ./input.txt api:/tmp/input.txt
rsbx cp api:/tmp/output.txt ./output.txt
```

A workspace ending in `:ro` is mounted read-only. `cp` transfers regular files and directory trees. Guest paths must be absolute. The implementation rejects traversal and unsupported file types; source symlinks are rejected unless link following is explicitly enabled.

Workspace paths are host paths. Only add directories the agent needs. A writable workspace lets guest processes change those host files; `:ro` prevents writes through that mount but does not hide files inside the guest image.

## Environment and secrets

```sh
rsbx exec -e MODE=debug api env
rsbx secret set openai --sandbox api
rsbx secret ls
rsbx secret rm openai --sandbox api
```

Use `-e KEY=VALUE` for a session override. Values passed on a command line may be visible in host process arguments; do not pass secrets that way. `rsbx env plan [PATH...]` provides a static, read-only preview. Without paths it reads `sbxenv.yaml` from the current directory and merges optional `~/.sbxenv.yaml` defaults first. Explicit file or directory paths merge in order and skip user defaults. YAML values support `${{ env.projectDir }}` and `${{ env.fileDir }}`. The preview lists declared ports but does not bind them. Declared `args` are checked with `--env-arg` and `--env-args-file`; values are redacted in the preview. Combined argument input is limited to 8 MiB and 20,000 values. Direct `--env-arg` values can appear in process listings, so use an argument file for sensitive values. Declared `${{ env.args.NAME }}` references are expanded once in YAML values; kit arguments are not implemented. `--name NAME` overrides the previewed sandbox name. Environment values are masked in previews. `rsbx env create [PATH...]` creates a local sandbox from the supported subset: agent, name, workspace mounts, ports, environment variables, and CPU/memory options. It asks for approval in a terminal; use `--force` for a one-command approval in non-interactive scripts. `rsbx env run` creates a missing sandbox or attaches to a matching existing one; `--detach` starts without attaching. `rsbx env exec` runs a command in a matching existing sandbox and starts it if stopped. `rsbx env rm` removes only the sandbox matching the declared name, agent, and workspaces. Kits, credential bindings, host commands, and MCP declarations remain unsupported and fail closed. Environment lifecycle execution has command and unit-test coverage; full cross-platform Docker parity and live runtime acceptance remain open. `rsbx run --env` applies values to one run/session and is not an environment-file workflow. `rsbx secret` stores provider values in the host credential vault and keeps them out of SQLite and logs. Read the [security model](security.md) before enabling secret proxy features. Docker account sign-in is separate and is described in [Docker and Gyrel](docker.md).

## Network and ports

```sh
rsbx run --publish 127.0.0.1:8080:3000 shell .
rsbx ports api
rsbx policy ls api
rsbx policy org
```

New sandboxes default to the `allow-all` egress profile, matching Docker `sbx`: TCP and UDP to `0.0.0.0/0`, subject to explicit deny rules. `deny-all` remains selectable with `--policy-profile deny-all`, `rsbx policy init deny-all`, or `policy.profile`. Explicit deny rules still win over allows, organization deny rules keep precedence over local rules, and every fail-closed control is unchanged. A sandbox with `deny-all` cannot use outbound networking until a rule permits it.

The gateway policy layer supports HTTP conditions for method (an exact list or `ANY`), path globs, and query parameters. The local `rsbx` policy surface does not expose those fields yet, so `rsbx run` and `rsbx policy` cannot author them in this alpha. Where such conditions exist, they are evaluated on the bounded HTTP request head; a rule whose conditions cannot be evaluated does not match and never widens to the whole destination. Deny rules are evaluated before allow rules. An allow and deny rule with the same selector in the same scope are rejected with a typed conflict error naming both rules. Live `gvproxy` datapath enforcement of HTTP conditions remains unverified, so do not treat an HTTP rule as a proven packet filter.

`rsbx policy org` shows the organization policy that is in effect: org, bundle identity, enforcement state, and every rule marked enforced or advisory (human table or `--format json`). Explicit policy supports IPv4 CIDR and domain targets where the configured gateway supports them. Port publishing is limited to host loopback addresses; public host bindings are rejected. A successful `--publish` setup does not grant the guest outbound access. `rsbx policy check` evaluates stored rules; it is not a live query to the gateway and does not prove that a packet will pass.

## Daemon lifecycle {#daemon-lifecycle}

```sh
rsbx daemon start --detach
rsbx daemon status
rsbx daemon log-level
rsbx daemon stop
rsbx daemon restart --detach
```

`rsbx daemon` manages the local `sandboxesd` process. `start` and `restart` run in the foreground unless `--detach` is passed, and accept `--policy allow-all|balanced|deny-all` to initialize the global profile. `status` reports the live endpoint, daemon version, API version, socket and log path, and sandbox counts. `status --json` uses the sbx field names `status`, `socket`, and `logs`, plus the available PID, version, API, and count fields. `log-level` shows the `general`, `proxy`, and `all` categories; `log-level set TARGET LEVEL` persists a change without restarting the daemon.

The state directory and log path are derived from `--socket`. The CLI passes `--state` and `--socket` to the daemon and finds `sandboxesd` on `PATH` or beside `rsbx`; set `SANDBOXES_DAEMON_BINARY` to select another binary. A daemon started separately with explicit VM runtime flags, as in the [quick start](quickstart.md), keeps its own process lifecycle. `rsbx daemon stop` and `rsbx daemon restart` apply the identity checks below; if no control record identifies that daemon and the platform cannot discover the socket peer, the command reports an ambiguous state instead of guessing.

`rsbx daemon stop` signals only a daemon whose identity it can prove. A daemon started outside `rsbx daemon start` is stopped when its identity is proven from the live socket peer. If that cannot be proven, stop refuses without signaling and prints an actionable message. Inspect the process that owns the socket, stop it manually with `SIGTERM`, and verify the endpoint before removing it. On platforms that cannot discover the socket peer, the command decides from the control record instead. `restart` uses the same checks before starting a new daemon. Stale sockets and control records are not removed silently.

## Docker

The CLI accepts `--docker` for an opt-in guest Docker profile. It can start `dockerd`, but nested `docker run/load/build` and Compose remain blocked by guest `unshare` restrictions in the current runtime. This does not mean the VM fails to start. `rsbx login` stores Docker account authorization on the host; it does not forward registry credentials into the guest. Read the [Docker guide](docker.md) for the current status and history.

## Host setup and helpers {#host-setup-and-helpers}

```sh
rsbx setup
rsbx skills list
rsbx skills import ./my-skill
rsbx completion zsh
```

`setup` is a read-only host readiness report (platform, daemon socket, runtime assets, required binaries, Docker CLI) with `--format json`; it installs nothing and does not claim a VM can boot. `setup` and `skills` remain marked experimental in their command help. `skills` manages host-side agent skill sources (`list`, `import`, `remove`) and never writes into a sandbox workspace. `import` without a path scans the six supported agent directories and `--dry-run` previews them. `rsbx run --skills=readonly` or `rsbx create --skills=readonly` shares the store read-only with a new sandbox. `readwrite` is rejected until a safe per-agent target exists, and guest delivery is not yet qualified on every platform. `completion` prints a script for bash, zsh, fish, or powershell.

Cloud commands (`move`, `ttl`, `volume`) are out of scope for the local alpha and remain unsupported. Windows WHP is not implemented.

## Exit codes

Refusals carry a machine code and a nonzero exit status. The same code appears on stderr and in `--format json` records when the command emits them.

| Code | Exit status | Meaning |
|---|---|---|
| `0` | 0 | Command completed; no refusal. |
| `1` | 1 | Partial failure: an action ran and at least one item failed, was skipped, or was stale. |
| `2` | 2 | Pre-flight refusal: validation failed and no action was taken. |
| `125`–`127` | 125–127 | Reserved for `exec` command-status parity. |
| `NOT_OWNED` | 1 or 2 | The resource does not belong to this daemon installation. |
| `PATH_ESCAPE` | 1 or 2 | A path resolves outside the permitted state root. |
| `FILTER_REQUIRED` | 2 | `prune` needs a filter or `--all` before deletion. |
| `STALE` | 1 | A planned item changed before execution and was skipped. |

The registry is the source for machine codes; a code that is not registered does not document a refusal.

## Get exact options

Use the binary's built-in help for the version you installed:

```sh
rsbx --help
rsbx run --help
rsbx policy --help
rsbx daemon --help
```

The product is alpha software, so flags and behavior can change between releases. Check installed-binary help before relying on a command.
