# Documentation control ledger

`ledger.jsonl` is the machine-readable evidence ledger behind the comparison
page and the `[control: ID]` references in the docs. `scripts/docs-lint.py`
resolves every reference against this file. A reference to a missing or
pending entry fails the documentation build.

## Row schema

Each line is one JSON object. One row is one control record.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable control id used by `[control: ID]`. |
| `control_class` | yes | `E1` same-input live, `E2` state assertion, `E3` negative control. |
| `status` | yes | `recorded` or `pending`. Only `recorded` ids resolve in docs. |
| `title` | yes | Short human label. |
| `date` | recorded | Control date in ISO form. |
| `runner` | recorded | Person or agent that ran the control, plus re-runs. |
| `components` | recorded | Component versions and SHA-256 digests. Use `null` when the evidence does not record a digest. |
| `scope` | yes | What the control exercised and what it did not. |
| `source` | yes | `probe`, `b0`, `v1`, `v3`, `p15`, `r5`, `r6`, `comparison-manifest` or `self-test`. |
| `commands` | no | Commands or test selectors that produced the evidence. |
| `command_pair` | E1 | The same-input command pair on both binaries. |
| `artifacts` | recorded | List of `{path, sha256, scope}` records. |
| `pending_for` | pending | The control that is still missing. |

## Artifact scope

`scope: repo` artifacts live in this repository and are checked for existence
and digest on every lint run. `scope: external` artifacts are recorded host
captures. CI does not have those paths, so absence is not an error there; when
the file is present locally, its digest is checked.

## Rules

- Seed rows only from an existing recorded artifact. Do not infer, reconstruct
  or invent a result.
- Keep a missing control as a `pending` row. Pending rows are not evidence and
  cannot be cited.
- A component version or digest that the artifact does not record stays `null`,
  with the gap named in `notes`.
- Do not move a comparison row to a stronger status until the ledger entry and
  the required control exist. The comparison page is the reviewer-facing view;
  this file is the source.
