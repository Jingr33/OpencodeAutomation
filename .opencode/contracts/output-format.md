# Output Format Contract

The JSON result is the canonical interface for every command. Human-readable
output is a presentation of the same result and MUST NOT contain information
that is absent from the JSON result.

## Result envelope

Commands MUST emit one result envelope after execution (or after a validated
failure):

```json
{
  "schema": "opencode.result/v1",
  "command": "namespace.command",
  "status": "succeeded",
  "operationId": "generated-operation-id",
  "target": {},
  "input": {},
  "preview": {},
  "authorization": {},
  "phases": [],
  "result": {},
  "errors": [],
  "warnings": [],
  "startedAt": "2026-01-01T00:00:00Z",
  "finishedAt": "2026-01-01T00:00:01Z",
  "durationMs": 1000
}
```

The `schema` value MUST be exactly `opencode.result/v1`. `command`, `status`,
`phases`, `errors`, and `warnings` are always present. Optional values MUST be
represented as `null` or an empty array/object according to this schema, not by
changing the field name. Timestamps MUST be UTC RFC 3339 strings. Durations
MUST be non-negative integers in milliseconds. `operationId` identifies one
attempt and MUST NOT be reused for a retry.

`input` MUST contain normalized, non-secret inputs. Passwords, access tokens,
private keys, authorization headers, and credential-bearing URLs MUST be
omitted or redacted. The `target` object follows
[target-context.md](target-context.md).

## Statuses and exit codes

The top-level status MUST be one of:

| Status | Meaning | Recommended exit code |
| --- | --- | ---: |
| `succeeded` | All required actions completed and were verified. | 0 |
| `planned` | A preview completed; no mutation was authorized or performed. | 0 |
| `unchanged` | The requested state already existed and verification succeeded. | 0 |
| `cancelled` | The user declined or did not provide required authorization. | 2 |
| `blocked` | A precondition or safety policy prevented execution. | 3 |
| `partial` | Independent actions had mixed outcomes. | 4 |
| `failed` | The command could not complete and no success can be claimed. | 1 |
| `unknown` | An external effect may have happened but state could not be verified. | 5 |

Commands MUST use these meanings consistently. A command MAY use a different
nonzero process exit code only when it documents the mapping in its own
contract. The exit code MUST never turn a `partial` or `unknown` result into
success.

## Phase records

Each phase record MUST contain:

```json
{
  "name": "preview",
  "status": "succeeded",
  "startedAt": "2026-01-01T00:00:00Z",
  "finishedAt": "2026-01-01T00:00:00Z",
  "actions": [],
  "reason": null,
  "errorCodes": []
}
```

`name` is one of the phases in [command-contract.md](command-contract.md).
`status` is `succeeded`, `skipped`, `failed`, `blocked`, `cancelled`, or
`unknown`. Every required phase MUST be present, including phases not reached.
An action record SHOULD include a stable `id`, resource, intended operation,
and item status (`planned`, `applied`, `unchanged`, `skipped`, `failed`, or
`unknown`).

## Preview and authorization records

`preview` MUST state whether it was generated, the plan version, affected
resources, intended side effects, and whether the plan is stale. For example:

```json
{
  "generated": true,
  "planVersion": "sha256:...",
  "actions": [],
  "sideEffects": [],
  "stale": false
}
```

`authorization` MUST state `required`, `mode` (`not_required`, `dry_run`,
`apply_flag`, or `interactive`), `provided`, and `scope`. Authorization MUST
identify the plan it approved; an authorization for a different target or
plan is invalid.

## Errors and warnings

Each error MUST use this shape:

```json
{
  "code": "target_required",
  "message": "An explicit target repository is required.",
  "phase": "resolve",
  "retryable": false,
  "action": "Select a repository with --repo or OPENCODE_TARGET_REPO.",
  "details": {}
}
```

`code` is stable and suitable for automation. `message` is safe for users and
MUST NOT contain secrets. `phase` identifies where the error occurred;
`retryable` is true only when retrying after the same state is safe. `action`
SHOULD explain how to recover. `details` MUST be sanitized and MAY be empty.
Warnings use the same shape but MUST NOT claim that a command failed.

## Text presentation

When `--format text` is selected, output MUST contain these headings in order:

```text
Command:
Status:
Target:
Preview:
Actions:
Verification:
Errors:
Warnings:
```

The text form MAY be concise, but it MUST include the final status, affected
target, changed or unchanged resources, failed/skipped checks, and recovery
action. `--format json` MUST write only the single JSON envelope to stdout;
diagnostic logging belongs on stderr.
