# CLI reference

The released user-facing command is `rsbx` v0.0.64. It talks to the local `sandboxesd` daemon. Use `rsbx COMMAND --help` for exact flags in the installed binary.

## Everyday workflow

```sh
rsbx version
rsbx run shell .
rsbx ls
rsbx stop NAME
rsbx exec NAME -- /bin/sh
rsbx rm NAME
```

`run` creates, starts and attaches. The current directory is its default workspace; `--detach` exits after start. Pass agent arguments after `--`. `--name` selects an existing named sandbox; `--new` forces creation and `--replace` recreates a named sandbox. `--clone` uses a private guest clone of a local Git root. Workspace paths may include `:ro`; `--deny-write PATH` adds a read-only subpath.

`create` differs from `run`: with no path, it creates **without** a workspace mount. Check the chosen command before giving an agent access to files.

| Area | Released commands | Current boundary |
|---|---|---|
| Sandbox | `run`, `attach`, `create`, `exec`, `cp`, `ls`, `stop`, `rm`, `prune`, `ports` | Local daemon only |
| Management | `agents`, `daemon`, `diagnose`, `env`, `login`, `logout`, `mcp`, `policy`, `reset`, `secret`, `settings`, `tui` | See each `--help`; not every Docker subcommand exists |
| Extensions | `kit`, `template`, `skills`, `setup` | Local kits; template inspect/list; `setup` is read-only; `skills` manages a host store and supports `--skills=readonly` on create/run (readwrite is rejected) |
| Cloud | `move`, `ttl`, `volume` | Explicitly unsupported |

`--help` uses the same section layout as Docker `sbx` (`Description`, `Usage`, `Aliases`, `Examples`, `Flags`), and the documented aliases work: `list`, `remove`, `delete`, `secrets`. Docker `sbx` has no `start`, `get` or `wait`; we removed ours so the surface matches, and `run`/`exec` start a stopped sandbox themselves. `rsbx policy ls` reports the reference baseline rules for `allow-all` (`default-allow-all`, filesystem read/write) in the `POLICY / SOURCE / APPLIES TO / SUMMARY` table.

`--policy-profile` defaults to `allow-all`; use an explicit profile for narrower egress. Host hooks and secrets require their own trust decisions. See [security and limits](limits.md) and the [Docker comparison](comparison.md).

## Rheic extensions

The following behavior is specific to Rheic in this comparison with Docker `sbx` v0.50.1:

- `rsbx attach NAME` attaches to a local sandbox; Docker `sbx attach` is cloud-only. Rheic's `attach --shell` starts `/bin/sh` instead of the agent.
- `rsbx ls --limit N` limits the number of returned sandboxes. `rsbx stop --grace DURATION` sets the stop grace period.
- The local settings catalog includes `dns.upstream`, `policy.profile`, `defaults.cpus`, `defaults.memory_mib`, and `mcp.remote.allowedHosts`. These are Rheic settings; they are not Docker `sbx` settings.

These extensions do not establish compatibility for the rest of each command. See the [comparison](comparison.md) for confirmed gaps and untested behavior.
