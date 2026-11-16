# Docker and Rheic

Rheic currently has two separate Docker-related features: Docker account sign-in on the host, and an experimental option for running Docker Engine inside a sandbox. They are different features. Signing in does not make a guest Docker daemon available.

## Current status

**The opt-in profile can start a guest Docker daemon, but nested workload operations remain blocked in the current alpha.** `docker run`, `docker load`, `docker build`, and Compose fail while setting up nested workloads because `unshare` is not permitted. This does not mean the VM fails to start. The profile does not grant broad guest cgroup or capability access to make those operations work; that design was rejected. Do not rely on nested workload operations until a guest-scoped, least-privilege design has passed review and tests.

## Docker account sign-in

The CLI stores Docker account authorization through the local daemon. The alpha also contains an experimental host broker for Docker Hub guest pulls and pushes. It has synthetic contract coverage, but it has not passed live VM acceptance or a same-version `sbx` comparison. Do not treat it as production-ready or as Docker Sandboxes parity. Other registries are not supported by this path. Registry traffic remains subject to the sandbox network policy: new sandboxes default to allow-all, so explicit deny rules or a `deny-all` profile can still block the broker.

For browser-based device authorization:

```sh
rsbx login
```

The CLI prints a verification code and URL. Complete the authorization in your browser. For a Docker Hub personal access token (PAT), pass the token through standard input so it is not included in command arguments:

```sh
read -s DOCKER_PAT
printf '%s\n' "$DOCKER_PAT" | rsbx login --username YOUR_DOCKER_ID --password-stdin
unset DOCKER_PAT
```

`rsbx logout` asks for confirmation and stops running local sandboxes before removing the Docker account authorization. `rsbx logout --force` skips only the confirmation; it still stops running sandboxes. Read the prompt before confirming because running work is stopped.

## The `--docker` option

The CLI exposes `--docker` on create/run for an opt-in Docker workload profile. The profile is privileged and can start `dockerd`, but nested container operations are not currently functional or security-qualified. The option's presence in CLI help is not evidence that `docker run` or other workload operations succeed.

```sh
# Experimental: guest Docker workload commands are currently blocked.
rsbx run --docker shell .
```

A supported workflow requires a guest-only cgroup design, a minimal capability set, isolation tests, persistence and lifecycle checks, and independent security review. Runtime exec/PTY support exists, but it does not make nested guest containers work.

## How this differs from Docker Sandboxes

Docker Sandboxes provides its own agent-oriented sandbox workflow and Docker Engine integration. Rheic is a separate project with a local microVM runtime. It does not claim feature parity with Docker Sandboxes. In particular, nested guest workloads, registry credential forwarding, and production security qualification remain incomplete in the current alpha. Read the [security model](security.md) before relying on a feature.

## Related guides

- [Quick start](quickstart.md) — install the alpha and boot a microVM on macOS ARM64.
- [CLI reference](cli.md) — command syntax, workspaces, networking, and secrets.
- [Security model](security.md) — trust boundaries and known limitations.
