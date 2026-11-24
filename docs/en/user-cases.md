# User cases

These scenarios run against the alpha bundle on macOS ARM64 and show the exact commands plus the expected behavior — including the places where the alpha deliberately refuses. Commands assume `rsbx` and the daemon socket on their defaults; the state directory is `$HOME/.sandboxes` (override with `RHEIC_STATE_DIR`).

## Project review sandbox

```sh
cd ~/code/my-project
rsbx run shell .
```

`run` creates or reuses a sandbox for the current directory, starts the VM, and attaches a guest shell. The project is mounted read-write at the same path inside the guest. Exit the shell with `Ctrl-D`; the sandbox keeps running until you stop it.

```sh
rsbx ls -q
rsbx stop <name> && rsbx rm -f <name>
```

Detached + scripted session:

```sh
rsbx run --detach --name review shell .
rsbx exec review -- git status --short
rsbx exec review -- sh -c 'cargo test 2>&1 | tail -5'
```

A stopped sandbox starts automatically on the next `exec`.

## Editing with an agent

```sh
rsbx run codex .
rsbx run claude ~/code/my-project
```

Agent sessions read provider credentials from the host vault; the guest only ever receives a placeholder reference. This path is preview: launch probes passed, full provider login per agent is not yet qualified — see [agents](agents.md).

## Sharing the same project across agents

```sh
rsbx run --name alice claude ~/code/my-project
rsbx run --name bob codex ~/code/my-project
```

Every sandbox gets its own VM and its own workspace view; there is no shared writable state between them unless you mount a workspace explicitly. Cross-VM isolation passed live acceptance.

## Copying files in and out

```sh
rsbx cp ./patch.diff review:/tmp/patch.diff
rsbx exec review -- git -C $PWD apply --check /tmp/patch.diff
rsbx cp review:/tmp/report.html ./report.html
```

`cp` works in both directions and refuses symlink escapes at the boundary.

## Publishing a port

```sh
rsbx run --detach --name web shell .
rsbx run -p 8080 --name web2 shell .    # or `-p 8080:3000` for a fixed pair
rsbx ports web
```

The gateway publishes `127.0.0.1` host ports. Publishing a port already in use fails with a clear conflict and changes nothing.

## Freezing an environment as a template

```sh
rsbx run --detach --name lab shell .
rsbx exec lab -- sh -c 'pip install pandas==2.2.3'
rsbx stop lab
rsbx template save lab pandas-lab
rsbx template ls
rsbx template export pandas-lab ./pandas-lab.tar
```

Templates are OCI layer diffs with whiteout and opaque-directory semantics; exported archives never contain your host workspace files. Booting `rsbx run --image docker.io/library/pandas-lab:v1 …` reuses the local image without a registry pull. Guest-resident credentials inside the captured filesystem are warned about on save.

## Credentials with host vault

```sh
rsbx secret set openai                       # interactive paste, value stays on host
rsbx secret ls
rsbx secret set-custom --host api.example.com --env API_KEY
```

`set-custom` prints the generated placeholder once so you can wire it into configs; `secret ls` shows only the masked tail. Inline values never appear in daemon logs or the state database. `rsbx secret rm` deletes the vault entry and invalidates subsequent substitution — an in-flight request finishes, later requests do not receive the secret.

Reference and command sources (`--ref op://…`, `--command /usr/local/bin/token-helper`) create a consent request instead of storing anything, and granting waits for a trusted OS-backed approval — so `approve` fails closed today.

## Reviewing consent requests

```sh
rsbx mcp add docs --url https://mcp.example.com/mcp
rsbx policy approval ls
rsbx policy approval inspect <ID>
rsbx policy approval respond <ID> --option deny
```

The MCP registration answers with a challenge ID and stores nothing until consent. `inspect` shows the destination host/path, header names and their vault classification — never values. Approving requires the OS-backed consent provider (pending); denying always works and is recorded.

## Declaring a reusable kit

```sh
mkdir my-kit && cat > my-kit/spec.yaml <<'YAML'
apiVersion: rheic.dev/v1alpha1
kind: Kit
metadata:
  name: my-kit
spec:
  agent: shell
YAML
rsbx kit validate ./my-kit --offline
rsbx kit pack ./my-kit
```

`pack` writes a deterministic ZIP (sorted entries, pinned timestamps, no symlinks, no overwrites). Without `--offline` validation also runs the daemon kit policy (`kit.allowedSources`, `kit.allowLocalKits`, `kit.requireSignature`) and prints which setting decided a denial.

## Network policy checks

```sh
rsbx policy allow network api.openai.com --sandbox web
rsbx policy check network api.openai.com --method GET --sandbox web
rsbx policy ls web
```

`check` is evaluated against the stored rules and says allow or deny without touching the network. Deny wins, and org-managed rules can only tighten local ones.

## Live events in the terminal

```sh
rsbx tui
```

Press `2` for the event stream (operation progress and lifecycle changes) and `3` for sandbox logs. The panels show a bounded tail with a drop counter; switching panels cancels the underlying stream.

## Recovering after a hard kill

```sh
kill -9 <daemon-pid>          # abrupt loss, like a crash
bin/rheicd-launch.sh          # next start reconciles automatically
```

On startup the daemon reconciles create journals: resources it can prove it owns (marker token match) are cleaned up; anything it cannot prove is left untouched and reported in the log. Nothing is deleted speculatively.

## Verifying the runtime was not replaced

```sh
printf 'x' | dd of=~/.sandboxes/…/runtime/bin/ctr bs=1 seek=5000 conv=notrunc   # any tampered bundle binary
rsbx run shell .
```

Expected:

```text
error: runtime artifact "ctr" … SHA-256 mismatch … refusing to launch an unverified artifact
```

Restore the original bytes (or rebuild digests) to proceed.

## What is not covered yet

Windows and native Linux hosts, rootless, and nested Docker in guests; agent provider logins per built-in; interactive OAuth for remote MCP servers and the OS consent prompt for approvals; L7 HTTPS interception; cloud commands. All of these fail closed or are out of scope for the alpha.
