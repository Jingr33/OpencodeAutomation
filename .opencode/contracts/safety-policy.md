# Safety Policy

This policy is the baseline for all automation commands. Safety decisions are
enforced by command implementations and helper scripts, not only by prompt
wording. A command MUST stop when it cannot prove that the requested operation
is within its declared scope.

## Operation classes

Every command MUST declare one class:

| Class | Examples | Authorization |
| --- | --- | --- |
| Read-only | Inspect files, Git status, fetch metadata, render a plan. | No mutation authorization; report all network reads. |
| Reversible mutation | Create a branch/worktree, write a generated report, add an Issue label. | Preview and explicit authorization. |
| Mutation | Edit tracked files, create an Issue/comment, commit, push, start a process. | Preview, explicit authorization, and post-action verification. |
| Destructive mutation | Delete files/worktrees, force operations, close an Issue, stop a process owned by another operation. | Preview, explicit confirmation naming the exact target and action, and all class-specific safeguards. |

The least powerful class that describes an operation MUST be used. A command
MUST NOT hide a mutation inside a read-only or preview operation.

## Preview and authorization

Before every reversible, mutating, or destructive operation, the command MUST
produce a preview containing:

- canonical target and repository identity;
- branch, worktree, or remote resource affected;
- exact files, records, commands, or processes to be changed;
- intended values and relevant defaults;
- side effects, risks, and any irreversible step;
- preconditions and verification checks; and
- the authorization required and its scope.

The command MUST then receive explicit authorization that refers to that
preview. `--apply` is acceptable only when the command has printed or otherwise
recorded the complete preview in the same operation. Interactive confirmation
MUST name the exact resource and action. A broad instruction to “implement the
Issue” does not authorize commit, push, deletion, or remote mutation unless the
specific command contract says so. If authorization is absent, the command
MUST return `cancelled` or `planned` and perform no mutation.

Preview and execution MUST use the same normalized arguments. The command MUST
revalidate target identity, branch/worktree attachment, file/resource state,
and authorization scope immediately before mutation. Changed state invalidates
the preview.

## Target and filesystem boundaries

Commands MUST follow [target-context.md](target-context.md). They MUST NOT:

- guess between repositories, branches, worktrees, or service roots;
- operate on a path outside the resolved target without an explicit second
  target and contract permission;
- follow a symlink out of an approved boundary for a write or deletion;
- treat an external repository as a managed cleanup candidate;
- recursively delete a repository clone as a convenience operation; or
- use a path derived only from a branch name without collision checks.

Managed local repositories MUST stay below `OPENCODE_SOURCE_ROOT` and use the
repository's ownership/state records. External repositories MUST remain at the
user-selected path and MUST never be removed by automation. Deletion MUST be
itemized, previewed, authorized, and revalidated immediately before each item.

## Git and worktree rules

Automation MUST NOT reset, clean, force-push, overwrite uncommitted work, or
remove a worktree containing changes without a separate destructive contract
and explicit confirmation. A cleanup operation MUST additionally prove that
the worktree is managed, is not the main worktree, has no tracked, untracked,
or ignored changes, has no local stash entries, has a reachable remote and
upstream branch, and has no local-only commits. Missing, unreachable, or
ambiguous remote state is a hard stop, never permission to delete.

Commit, push, pull-request creation, and Issue mutation are separate side
effects. A command MUST NOT infer authorization for one from authorization for
another. Creating a worktree MUST NOT claim to switch the active OpenCode
session.

## Command and remote execution

Local and remote commands MUST prefer argument arrays over shell strings. Shell
syntax MUST be opt-in, documented, and escaped for the selected platform.
Timeouts, cancellation, output limits, working directories, environment
variables, and overwrite behavior MUST be explicit. Remote operations MUST
remain below the configured remote root and MUST report the exact remote host
and path in their preview.

Process launches MUST record ownership, command, working directory, process
group, logs, and lifecycle state. A stop operation MUST NOT terminate an
unrelated process based only on a reused PID, port, or name.

## Secrets and data handling

Credentials MUST come from approved environment variables, credential helpers,
or interactive authentication. They MUST NOT be written to source files,
command arguments when avoidable, summaries, Issue comments, logs, or result
records. Remote URLs containing credentials and sensitive environment values
MUST be redacted. Captured output MUST be bounded and sanitized before it is
posted externally.

## Failure and recovery

Safety or precondition failures MUST stop before mutation and return a stable
error. If an external operation may have succeeded but cannot be verified, the
result MUST be `unknown`; the command MUST NOT retry it automatically. Partial
success MUST preserve completed work, list every item outcome, and provide a
safe reconciliation or retry action. Rollback MUST NOT be claimed unless it was
actually performed and verified.

Commands MUST leave enough state to explain what happened, but MUST NOT retain
secrets or unbounded logs. A summary SHOULD be written below the configured
support root and MAY be posted to GitHub only after redaction.

## Least privilege and status

An agent or command MUST have only the tools and permissions required for its
declared operation. Review and verification operations are read-only by
default. Implementers MUST NOT commit, push, reset, clean, or delete unless a
separate explicitly authorized operation is invoked. A command MUST report
`succeeded` only after verification; otherwise it MUST use `planned`,
`cancelled`, `blocked`, `partial`, `failed`, or `unknown` as defined in
[output-format.md](output-format.md).
