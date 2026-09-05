# Command Contract

This document defines the contract every OpenCode Automation command MUST
follow. It applies to commands in this repository and to commands loaded for a
target repository. A command may add stricter rules, but it MUST NOT weaken
these rules.

## Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are
normative. A requirement using one of these words is testable and is not an
instruction for the model to interpret loosely.

## Command identity and input

Every command definition MUST document:

1. Its fully qualified name, purpose, and contract version.
2. Exact syntax, including positional arguments and supported flags.
3. The type, allowed values, and default for every argument and flag.
4. Whether unknown arguments, missing arguments, and extra positional arguments
   are rejected.
5. The target-resolution mode and all required preconditions.
6. Its operation class: read-only, reversible mutation, mutation, or
   destructive mutation.
7. Its preview, authorization, side-effect, partial-failure, and output rules.

Arguments MUST be parsed before any target inspection or mutation. Unknown or
ambiguous input MUST fail with a structured `invalid_input` error. A command
MUST NOT infer a value that has an explicit flag but an invalid or empty value.
Defaults MUST be documented and applied identically in preview and execution.

Unless a command explicitly documents another form, the supported common flags
are:

```text
--repo <absolute-path|registered-name>  target repository
--format <text|json>                   presentation format; default: text
--dry-run                              preview only; never apply changes
--apply                                authorize the displayed preview
```

`--dry-run` and `--apply` are mutually exclusive. A command MAY use an
interactive confirmation instead of `--apply`, but it MUST record the exact
authorization in its result. Phrases in ordinary task text such as “go ahead”
MUST NOT be treated as authorization for a mutation unless the command
explicitly defines that input as its confirmation mechanism.

## Required execution phases

Commands MUST execute these phases in order. A phase that is not applicable
MUST still produce a `skipped` phase record with a reason.

| Phase | Required behavior |
| --- | --- |
| `parse` | Validate syntax, flags, types, and defaults. No repository or remote mutation. |
| `resolve` | Resolve one target context using [target-context.md](target-context.md). Ambiguity is a hard failure. |
| `preflight` | Check repository identity, branch/worktree state, credentials, dependencies, and other documented preconditions. |
| `plan` | Calculate the intended actions from the validated inputs and current state. The plan MUST be deterministic for the same observed state. |
| `preview` | Present the target, actions, affected resources, authorization requirement, and known risks. Preview MUST complete before a mutation. |
| `authorize` | Require the command's documented explicit authorization for a mutation. Read-only commands MAY record `not_required`. |
| `execute` | Perform only the authorized actions. Each action MUST be independently identifiable and recorded. |
| `verify` | Re-read the affected state and check the command's completion criteria. Verification failure is not success. |
| `report` | Emit the stable result defined in [output-format.md](output-format.md), including every skipped, completed, and failed phase. |

No `execute` phase may run when `parse`, `resolve`, `preflight`, `plan`, or
`preview` fails. A dry run ends after `preview` with status `planned` and MUST
not create commits, branches, Issues, comments, files, processes, or remote
side effects. Reading state required to construct the preview is allowed.

## Preconditions and state revalidation

The command contract MUST state whether it requires a clean worktree, a
particular branch or default branch, an available remote, authentication, a
configured project, or a specific file/configuration. Preconditions MUST be
checked against the resolved target, not against the framework checkout by
accident.

Any state that can change between preview and execution MUST be revalidated
immediately before the affected action. If it changed, the command MUST stop
and return `stale_preview`; it MUST NOT silently apply the old plan. A rerun
MAY create a new preview.

## Side effects and idempotency

The contract MUST list all local, Git, GitHub, network, process, and filesystem
side effects. “No side effects” means no mutation of any of these categories.
Temporary files MUST be placed below the configured state/support area and
cleaned up unless the result says they were retained.

Commands SHOULD be idempotent. When a requested resource already has the
desired state, the command MUST report `unchanged` rather than performing a
duplicate mutation. A retry MUST use a fresh preflight and preview; it MUST NOT
replay an unverified partial plan blindly.

Creating a worktree does not change the current OpenCode session directory.
Commands MUST NOT claim that it does. A command that needs a different session
MUST report the path and the supported explicit way to open it.

## Partial failures

Commands that operate on multiple independent items MUST continue only when
the contract says an item is independent and safe to continue. Each item MUST
have its own result. On any partial failure the command MUST:

- stop dependent actions;
- preserve successful changes unless a documented, verified rollback exists;
- report the exact failed action and whether it may have had an external effect;
- report remaining work and a safe retry action; and
- finish with status `partial`, never `succeeded`.

An unknown outcome (for example, a network timeout after a remote mutation may
have occurred) MUST be reported as `unknown`, not retried automatically, and
MUST require state reconciliation before another mutation.

## Completion criteria

The contract MUST define observable completion criteria. A command is
`succeeded` only when every required phase completed, every required action
was verified, and no required item remains unresolved. It is `planned` for a
successful dry run, `blocked` when a safety/precondition rule prevents
execution, `partial` when some independent actions completed, `failed` when
no successful completion can be claimed, and `cancelled` when the user
declines authorization. These statuses and their exit-code mapping are defined
in [output-format.md](output-format.md).
