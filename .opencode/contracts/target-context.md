# Target Context Contract

Target resolution produces one canonical context before a command inspects or
changes a repository. The resolver MUST fail closed rather than guess when
more than one target is possible.

## Resolution order

The resolver MUST use the first usable source in this order:

1. Explicit `--repo <absolute-path>` or an explicitly named registered
   repository.
2. `OPENCODE_TARGET_REPO`.
3. The current checkout, only when it is not the agentic repository.
4. A hard failure with `target_required` when the current checkout is the
   agentic repository and no target was selected.

An explicit argument always takes precedence over an environment variable.
The value from `OPENCODE_TARGET_REPO` MAY be an absolute local path or a
registered repository name, but it MUST resolve to exactly one repository.
Relative paths MUST be rejected at the command boundary; configuration files
MAY define relative paths only relative to their documented configuration root.

## Configuration

The resolver uses these configuration values. A relative default is resolved
against the agentic repository root and is canonicalized before use.

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENCODE_SOURCE_ROOT` | `./source` | Root below which managed repositories and worktrees are allowed. |
| `OPENCODE_TARGET_REPO` | unset | Explicit target path or registered repository name. |
| `OPENCODE_STATE_ROOT` | `.opencode/state` | Mutable registry, ownership, and operation state. |
| `OPENCODE_SUPPORT_ROOT` | `dev_support` | Local summaries, diagnostics, and other support output. |
| `OPENCODE_PROJECT_PROFILE` | unset | Explicit target project-profile path; otherwise the target's documented profile is considered. |

An unset value MUST use the documented default or remain unset; it MUST NOT be
filled from an unrelated working directory. State and support roots MUST be
kept separate from the target's source files unless a command explicitly
documents otherwise.

Commands operating on the agentic repository itself MUST identify that scope
explicitly. They MUST NOT obtain it by bypassing the fail-closed toolkit target
resolution rule.

## Canonicalization and validation

For every candidate the resolver MUST:

- expand the configured path and resolve symlinks before comparison;
- verify that the path exists and is a directory;
- run `git rev-parse --show-toplevel` and use the Git top-level directory;
- reject a path that is not a Git repository or whose identity is ambiguous;
- resolve the repository name, remote identity, current branch (or detached
  state), and worktree path; and
- include the configuration source that selected the candidate.

The canonical path, not the spelling supplied by the user, is used for all
subsequent comparisons and operations. A candidate that resolves outside the
selected repository MUST be rejected.

## Managed and external repositories

The resolver MUST return `managed` and `canonicalPath` fields.

| Kind | Definition | Required behavior |
| --- | --- | --- |
| Managed | A registered local repository or worktree below the configured `OPENCODE_SOURCE_ROOT` (default `./source`) and owned by this toolkit. | It MAY be considered by managed allocation or cleanup operations after ownership checks. |
| External | A user-selected repository outside the managed source root. | It MUST be used in place. It MUST NOT be copied, moved, or treated as an automated deletion candidate. |

The resolver MUST reject managed paths inside the agentic repository unless
they are below the configured source root. The source root itself MUST NOT be
used as a repository. External status MUST be explicit; absence of proof of
managed ownership means `managed: false`.

## Context record

The canonical context is a machine-readable record with these stable fields:

```json
{
  "canonicalPath": "/absolute/path/to/repository",
  "managed": false,
  "gitTopLevel": "/absolute/path/to/repository",
  "branch": "main",
  "detached": false,
  "worktreePath": "/absolute/path/to/worktree",
  "slot": null,
  "repositoryName": "example",
  "remote": {"name": "origin", "url": "https://github.com/org/example.git"},
  "configurationSource": "explicit_argument"
}
```

`slot` is an integer for a managed source/worktree slot and `null` otherwise.
Credential-bearing remote URLs MUST be redacted before they are returned or
logged. The record MAY contain additional fields, but these field meanings and
types MUST remain stable.

## Failure rules

The resolver MUST return a structured error for missing, invalid, inaccessible,
non-Git, ambiguous, or conflicting candidates. It MUST NOT silently fall back
to another source after an explicitly supplied candidate fails validation. A
missing target, agentic-repository fallback, path traversal attempt, or
repository identity mismatch is a safety failure and MUST prevent mutation.
