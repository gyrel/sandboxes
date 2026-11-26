# Alpha testing guide

You are running the local alpha. When something goes wrong, one command gives the
maintainers everything they need **without exposing your secrets**:

```sh
rsbx diagnose --bundle --out gyrel-diagnose.tar.gz
```

## What the bundle contains

- `manifest.json` — what was collected, sizes, digests, and an explicit list of
  anything that had to be left out
- `versions.json` — CLI and daemon versions (when the daemon is reachable)
- `platform.json` — OS/arch, virtualization support, required helper tools
- `config.redacted.json` — your settings **with secret-bearing values replaced**
- `sandboxes.redacted.json` / `policies.redacted.json` — inventory and policy
  **counts and rule targets only**
- `approvals.pending.redacted.json` — pending approval requests (identifiers and
  disclosure metadata, never values)
- `logs/daemon.tail.jsonl` — a bounded, timestamp-filtered daemon log tail
  (default window 24 hours, ≤2000 lines)
- `errors.json` — collector failures recorded as error classes
- `README.txt` — this contract, in text

## What it can never contain

Secret values, vault payloads, tokens, private keys, HTTP header values,
workspace file contents, environment dumps, SQLite databases, snapshots, and
absolute paths outside your own home (homes collapse to `~`). Before writing the
archive, every byte is scanned for these shapes; **if anything matches, the
bundle is refused** (exit 1) and no file is created. Refusal is a feature: it
means we found something that must not leave your machine, and we print only the
rule name and location.

Options: `--sandbox NAME` (scope to one sandbox), `--since 2h` (log window),
`--paranoid` (hash even sandbox and image names), `--verify BUNDLE` (re-scan an
existing archive before sharing it).

## Filing a bug

1. Open a [new issue](https://github.com/gyrel/sandboxes/issues/new?choose=the+template)
   using the **alpha bug report** template.
2. Attach `gyrel-diagnose.tar.gz` (drag into the form) and paste its SHA-256
   (`shasum -a 256 …`).
3. Include: OS/arch, `rsbx --version`, exact command, expected vs actual.

If `--bundle` refuses, attach the refusal output (it never contains values) and
file the issue anyway — the rule name alone is a valuable bug.

## Privacy note

The bundle is as private as the GitHub issue you attach it to. Do not file bugs
from shared machines; `--paranoid` exists if your sandbox names are sensitive.
