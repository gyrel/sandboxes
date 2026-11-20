# OpenCode

OpenCode is a built-in **preview** agent in the released CLI. It uses the pinned
Docker sandbox template and does not need a custom image for a first run.

## Check that it is available

```sh
rsbx agents ls
rsbx agents ls --format json
```

`opencode` must be listed as `preview`. If it is missing, the installed CLI is
older than the release that added it; upgrade instead of copying configuration
from another installation.

## Store provider credentials

OpenCode supports several providers. Store only the keys you intend to use;
Rheic adds proxy references for the matching providers automatically:

```sh
rsbx secret set openai
rsbx secret set anthropic
rsbx secret set google
rsbx secret set groq
rsbx secret set mistral
rsbx secret set openrouter
rsbx secret set xai
```

Each command prompts for the value, so the key is not written to shell history.
`rsbx secret ls` shows the stored services without values. An explicit
`--env OPENAI_API_KEY=...` (or another provider variable) overrides the proxy
reference for that run.

## Run OpenCode

```sh
# Current directory as the workspace, attach to the agent
rsbx run opencode .

# Named detached sandbox, then attach later
rsbx run --detach --name oc opencode .
rsbx run --name oc opencode .

# Pass an argument to the agent after --
rsbx run opencode . -- --help
```

The built-in entry automatically enables the Docker profile required by the
OpenCode template. A read-only workspace can be added with `:ro`; a private
guest clone is available with `--clone`. Guest skills can be shared read-only
with `--skills=readonly` (see the CLI page for the platform limits).

## If OpenCode is not in the built-in set

Confirm the binary version first:

```sh
rsbx version
```

For a CLI that predates the built-in entry, register a local custom agent in
`~/.config/rheic/agents.yaml` (or the file named by `RHEIC_AGENTS_FILE`):

```yaml
agents:
  - name: opencode
    image: docker.io/docker/sandbox-templates@sha256:f36f91fef60ee2035fe07a5467cf00409d6301071ed790aa0c80c91f5c958d68
    command: ["opencode"]
    status: preview
    docker: true
    notes: Pinned Docker sandbox template; host proxy credentials are configured by the CLI.
```

Use a digest-pinned image. A custom entry cannot shadow a built-in name; if
`opencode` is already built in, the file is ignored for that name. Restart the
CLI and check `rsbx agents ls`.

## Troubleshooting

- **Image pull fails:** sign in to the registry with `rsbx login`, or override
  the image for a controlled local test with `--image`.
- **Provider errors:** check `rsbx secret ls`, then pass the key explicitly with
  `--env` to isolate the proxy path. Do not paste keys into a shell history.
- **Wrong agent command:** use `rsbx run --name NAME opencode .` and pass agent
  arguments after `--`.
- **VM or Docker workload issues:** OpenCode does not change the documented
  runtime limits; nested Docker workloads and full Docker `sbx` parity remain
  unqualified.
