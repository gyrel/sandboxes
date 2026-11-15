# Workspaces and files

A workspace is a host directory mounted into a sandbox. A writable workspace lets processes in the guest change those host files. Add only the directories the agent needs. Runtime and daemon include exec/PTY paths, and a limited macOS VM-backed lifecycle test passed; these CLI options do not establish workspace safety or full agent parity on every platform.

## Choose what to mount

Use the current directory as the default workspace:

```sh
cd /path/to/project
rsbx run shell .
```

Pass additional directories after the agent name. Add `:ro` to mount a directory read-only:

```sh
rsbx run shell . /path/to/reference:ro
```

Use `--deny-write` to make a subdirectory read-only while its parent workspace remains writable:

```sh
rsbx run --deny-write ./secrets shell .
```

Omit all workspace paths for a mountless sandbox. A mountless sandbox still receives files from its image; it is not an empty filesystem.

## Work on a private clone {#clone-mode}

`--clone` gives the agent its own Git checkout instead of a writable mount of your repository. The source workspace is mounted read-only at `/run/sandbox/source`, and the agent works in a private clone inside the guest:

```sh
cd /path/to/project
rsbx run --clone shell .
```

The daemon creates the clone with hooks and credential helpers disabled. As with `sbx`, the clone is placed at the same absolute path the workspace has on the host, and `origin` stays pointed at the read-only source (`/run/sandbox/source`), so the agent can diff its work against the original.

While the sandbox is running, the CLI adds a host Git remote named `sandbox-<name>` to your repository. It points at a host-loopback endpoint served by the guest Git daemon (upload-pack only) and looks like `git://127.0.0.1:<port>/<repository>`, so you can fetch agent commits from the sandbox:

```sh
git fetch sandbox-api
git log --oneline sandbox-api/HEAD
```

Fetched branches are mirrored twice: under `refs/remotes/sandbox-<name>/*` and under `refs/sandboxes/<name>/*`. The mirror survives removal, so `rsbx rm` warns that commits still inside the clone are lost and how to recover a fetched one with `git branch LOCAL refs/sandboxes/<name>/BRANCH`.

`rsbx stop` withdraws that endpoint and clears it from the stored sandbox; `rsbx start` publishes it again, possibly on a different port, and the CLI refreshes the remote URL. `rsbx rm` removes the remote it created. A remote whose URL you changed by hand is preserved with an explicit error instead of being overwritten.

Clone mode has narrow requirements and fails closed otherwise:

- exactly one workspace, and it must be a real Git repository — a current directory with a `.git` file (a linked worktree) is rejected;
- the image must provide a working `git` client and `git daemon`;
- an existing non-empty destination directory is rejected instead of being reused.

## Copy files

Exactly one side of `rsbx cp` must be a sandbox path. Guest paths must be absolute:

```sh
rsbx cp ./result.json build:/tmp/result.json
rsbx cp build:/tmp/report.txt ./report.txt
```

The command copies regular files and directory trees. Symbolic links, hard links, and special files are rejected by default. `-L` follows a top-level source symlink; its target must stay within a mounted workspace when the source is inside one. Nested links remain rejected.

## Reuse a named sandbox

`rsbx run --name NAME` reuses the named sandbox and starts it if needed. Explicitly different workspace paths or read/write modes are rejected instead of silently changing the existing sandbox. Use a new name when you need a different mount set.

## Limits

Workspace mounts are direct host file access. A read-only mount prevents writes through that mount; it does not hide data in the guest image or protect a different writable mount to the same host path. Read-only mounts now ask the guest runtime for recursive read-only (`rbind:ro:rro`), so a nested submount under the repository is not silently writable; a guest that rejects the option fails the create instead of falling back to a weaker mount. Clone mode is validated end to end on an owned macOS ARM64 VM (create, read-only source, host fetch, stop/start, delete). Host crash cleanup and broad adversarial filesystem validation remain open work. See the [security guide](security.md) before mounting sensitive directories.
