# Settings

The CLI reads settings from `~/.config/rheic/settings.toml` by default (the directory name is kept from before the Gyrel rename). Set `GYREL_SETTINGS_FILE` to use another file (the legacy `RHEIC_SETTINGS_FILE` still works with a warning). Prefer `rsbx settings set` so the CLI validates and writes supported keys. The daemon accepts an explicit path with `--settings`; restart it after changing daemon-owned DNS or gateway settings. The state directory defaults to `$HOME/.sandboxes` and can be overridden with `GYREL_STATE_DIR`; the legacy `RHEIC_STATE_DIR` is still honored with a deprecation warning.

`rsbx settings ls` lists the full pinned Docker Sandboxes settings matrix (49 Docker keys plus 5 Gyrel extension keys). Every key reports its evaluated value, source (`default` or `override`), built-in default, type, restart requirement, and description. Unknown keys are rejected; values are validated against the key's type (`bool`, `int`, `string`, or `json`).

Keys the local runtime consumes today:

```sh
rsbx settings set dns.upstream 192.0.2.53:53
rsbx settings set policy.profile sbx-compat
rsbx settings set defaults.cpus 2
rsbx settings set defaults.memory_mib 2048
rsbx settings set sandbox.disk.dockerVolume 10g
```

Other catalogued keys are stored as validated overrides and reported by `settings ls`; they take effect as the corresponding runtime support lands. Use `rsbx settings get KEY --json` for the full record and `rsbx settings unset KEY` to remove an override. JSON and YAML records use the Docker `sbx` settings schema: `key`, typed `value`, `type`, `source`, typed `default`, `env_var` where Docker defines one, and `requires_restart` when a daemon restart is needed.

New sandboxes default to the `allow-all` egress profile, matching Docker `sbx`. Explicit deny rules, organization deny precedence, and every fail-closed control still apply. `deny-all` remains selectable through `--policy-profile deny-all`, `rsbx policy init deny-all`, or `policy.profile`. `balanced` is also available, and `sbx-compat` is the settings and kit alias for `allow-all`.

The DNS address above is an example from a documentation-only IP range; replace it with a resolver reachable through your configured gateway. Set `policy.profile` to `deny-all` when a workload must start without outbound access. Settings files contain configuration, not secret values; store credentials with `rsbx secret`. The daemon's flat file keys are `dns_upstream`, `default_policy_profile`, `default_cpus`, `default_memory_mib`, and `docker_volume_size`; they are not TOML tables.

For daemon paths and runtime flags, see [Quick start](quickstart.md) and the module runtime documentation. Flags vary with build and platform; use `sandboxesd --help` from the installed binary.
