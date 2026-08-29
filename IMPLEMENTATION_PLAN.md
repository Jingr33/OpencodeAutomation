# OpenCode Automation Improvement Plan

Status: Proposal for discussion

## Objective

Make the repository deterministic, safe, and reusable across arbitrary application
repositories. Natural-language prompts should orchestrate validated operations, not
leave important behavior to model interpretation.

The system must support project-specific behavior through explicit project profiles
and technology-specific startup skills, while keeping the shared automation generic.
It must also keep prompts for operating this agentic repository separate from prompts
used against target working repositories.

## Current Assessment

The repository currently contains:

- 29 command definitions
- 7 agents
- 9 skills
- 3 Python helper scripts
- 6 Markdown templates
- 4 instruction files
- `opencode.json`
- No automated test suite
- No project-profile system
- No process lifecycle manager for application startup
- No formal separation between agentic-repository prompts and working-repository prompts
- No managed `source/` slot layout for local repositories and worktrees

The primary problem is that many definitions use ambiguous terms such as:

- “relevant tests”
- “when possible”
- “as needed”
- “active repository”
- “startup command”
- “long-running process”
- “reviewed changes”

These terms must be replaced with explicit contracts, validation rules, and result
formats.

## Important Existing Risks

### Critical

1. Repository and worktree ownership is not defined. Local managed repositories and
   worktrees must live below the gitignored `source/` directory using the
   `<repo_name>_slot<worktree_number>` convention. User-selected external paths must
   remain usable but must never be deleted by automation.
2. Worktree cleanup can remove worktrees for closed but unmerged pull requests.
3. Cleanup can remove local work before proving that the remote contains every local
   commit and that the worktree has no uncommitted or untracked files.
4. Cleanup behavior when no remote or upstream branch exists is not defined; it must
   stop and ask the user rather than delete anything.
5. Prompts for operating the agentic repository and prompts for operating target
   working repositories are not isolated by namespace or dependency set.
6. Startup commands do not track processes, logs, PIDs, ports, readiness, or
   shutdown.
7. Startup commands contain orchestration logic instead of being links to
   technology-specific startup skills.

### High

1. Commands do not consistently define arguments, defaults, preconditions,
   confirmations, side effects, errors, or outputs.
2. The review agent cannot inspect Git diffs with its current permissions.
3. Worktree creation does not switch the current OpenCode session into the new
   worktree.
4. Repository registration does not reliably verify the remote default branch.
5. Registry writes are not atomic or concurrency-safe.
6. Startup behavior depends on model interpretation.
7. Issue migration is not idempotent.
8. Synchronization commands have inconsistent confirmation behavior.
9. Cluster commands lack deterministic quoting, timeout, path, and overwrite rules.
10. Command names documented in the README must be verified against the installed
    OpenCode command-discovery behavior.

## Design Principles

1. Every command has a written input, output, error, and side-effect contract.
2. Every mutating operation has preview and explicit apply/confirmation behavior.
3. Shared automation never guesses a target repository when the target is ambiguous.
4. Explicit repository configuration takes precedence over automatic detection.
5. Automatic detection produces a preview and confidence/evidence, never silent
   irreversible behavior.
6. Safety must be enforced in scripts and permissions, not only in prompts.
7. Agents coordinate work; helper scripts validate and execute deterministic state
   transitions.
8. No command claims to change the OpenCode session directory unless it actually
   does so.
9. All generated state and summaries have stable, machine-readable fields.
10. Agentic-repository prompts and toolkit prompts are separate namespaces with
    separate instructions, skills, agents, and state contracts.
11. Local managed repositories use `source/<repo_name>_slot<N>` paths. External
    repositories are used in place and are never removed by automation.
12. Cleanup is permitted only after remote-commit completeness and local cleanliness
    are both proven.
13. Startup commands are routing links only; startup behavior belongs to the
    selected technology-specific toolkit skill.
14. Existing public command names should be preserved where practical, with aliases
    or a migration notice when names change.

## Phase 0: Contracts and Safety Baseline

### Deliverables

Create shared contract documentation:

```text
.opencode/contracts/command-contract.md
.opencode/contracts/target-context.md
.opencode/contracts/output-format.md
.opencode/contracts/safety-policy.md
```

Every command definition must specify:

1. Exact syntax and arguments
2. Allowed values and defaults
3. Target repository resolution
4. Preconditions
5. Preview behavior
6. Required confirmation
7. Side effects
8. Partial-failure behavior
9. Stable output format
10. Completion and failure status

Use `MUST`, `MUST NOT`, `SHOULD`, and `MAY` consistently.

### Target resolution

Define one resolution order:

1. Explicit `--repo <absolute-path>` or registered repository name
2. `OPENCODE_TARGET_REPO`
3. Current checkout, only when it is not the agentic repository
4. Fail closed when the current checkout is the agentic repository and no target
   is selected

A target may be either:

- A managed local repository under `source/`
- A user-selected external repository at an explicit local path

External repositories are used directly. They are never copied, moved, or removed
by this toolkit. The resolver must return a `managed` boolean and the canonical path.

Add and document:

```text
OPENCODE_SOURCE_ROOT=./source
OPENCODE_TARGET_REPO
OPENCODE_STATE_ROOT
OPENCODE_SUPPORT_ROOT
OPENCODE_PROJECT_PROFILE
```

All paths must be canonicalized. Managed paths must remain below `source/`; external
paths require explicit selection and must never be treated as deletion candidates.

### Prompt namespace separation

Use two strictly separate prompt namespaces:

```text
agentic_repo.*
toolkit.*
```

`agentic_repo.*` is reserved for commands, agents, skills, and instructions that
operate the agentic repository itself: repository registration, source-slot
allocation, worktree bookkeeping, framework configuration, and toolkit routing.

`toolkit.*` is reserved for commands, agents, skills, and instructions executed
against a target working repository: project inspection, implementation, review,
build, documentation, cluster work, and technology startup.

The implementation must use separate directories and dependency manifests for both
namespaces. Use the OpenCode-discovered roots while preserving physical separation:

```text
.opencode/commands/agentic_repo/agentic_repo.*.md
.opencode/commands/toolkit/toolkit.*.md
.opencode/agents/agentic_repo/agentic_repo.*.md
.opencode/agents/toolkit/toolkit.*.md
.opencode/skills/agentic_repo-*/SKILL.md
.opencode/skills/toolkit-*/SKILL.md
.opencode/instructions/agentic_repo/*.md
.opencode/instructions/toolkit/*.md
```

The exact command and agent discovery behavior must be verified against the installed
OpenCode version. If nested directories do not preserve the required names, retain
the same namespace prefixes in flat discovered filenames rather than relying on
implicit path naming.

`opencode.json` must load only the agentic-repository instruction set. Toolkit
instructions, skills, and agents are loaded explicitly for a selected target working
repository. No unprefixed shared prompt may be loaded implicitly. Any bridge from an
`agentic_repo.*` startup command to a `toolkit.*` skill must be explicit and limited
to that named startup skill.

### OpenCode metadata

- Assign an explicit agent to every command.
- Use the OpenCode built-in `build` agent; do not create a repository-defined build
  agent.
- Verify command names using the installed OpenCode version.
- Correct README examples to match actual command discovery.
- Define a consistent `--dry-run` / `--apply` policy.

## Phase 1: Core Infrastructure

### Target and state management

Implement a shared target/context resolver, preferably in:

```text
.opencode/scripts/context.py
```

It should return:

- Agentic repository root
- Target repository root
- Whether the target is managed or external
- Git top-level directory
- Current branch or detached state
- Worktree path and slot number, when managed
- Repository identity and remote
- Configuration source used

Managed repositories and worktrees must use this layout:

```text
source/<repo_name>_slot0
source/<repo_name>_slot1
source/<repo_name>_slot2
```

`source/` must be gitignored. Slot `0` is the local repository clone; additional
slots are worktrees associated with that repository. Slot numbers are allocated by
state, never derived from branch-name flattening, and must be collision-checked.

When a user supplies an external path, the resolver must use that path directly and
record `managed: false`. It must not copy the repository into `source/` and must not
include it in automated deletion or cleanup candidates.

Store mutable framework state below a configured state root. Use atomic writes and
locking for registries, slot allocation, and process records.

### Repository registry

Harden `repository.py`:

- Register and list repositories; do not implement automated repository removal.
- Derive managed clone paths below `source/<repo_name>_slot0`.
- Validate repository names and reject path traversal.
- Allow an explicit external path only when the user supplies it.
- Mark external entries as `managed: false` and exclude them from deletion logic.
- Prevent managed targets inside the agentic repository except `source/`.
- Reject or redact credential-bearing remote URLs.
- Verify requested source, origin, and default branch independently.
- Handle clone-success/registry-write-failure recovery.
- Write the registry atomically.
- Report stable JSON results.

Deleting the agentic repository itself is outside the toolkit's scope. Because
`source/` is gitignored and located inside the agentic repository, deleting the
agentic repository may delete managed local clones as normal filesystem contents.
External repositories remain untouched.

### Worktree management

Harden `worktree.py`:

- Allocate paths using `source/<repo_name>_slot<N>`.
- Validate repository identity and slot ownership before creating a worktree.
- Reject branch-name-derived path collisions.
- Canonicalize and validate explicit external paths.
- Reject path collisions before `git worktree add`.
- Detect branches attached to another worktree.
- Report main, detached, dirty, untracked, managed, and external state.
- Never remove an entire repository clone through worktree cleanup.
- Permit cleanup only for managed `source/` worktrees.
- Require a remote and an upstream branch for automatic cleanup.
- Fetch or otherwise verify the current remote state before evaluating cleanup.
- Require `git status --porcelain --ignored --untracked-files=all` to be empty. This
  includes tracked changes, untracked files, and ignored generated/dependency files.
- Require no local stash entries for the repository.
- Require zero local-only commits: local branch HEAD must not be ahead of its
  upstream remote branch.
- Require the remote branch to exist and be reachable.
- Treat a missing remote, missing upstream, fetch failure, or ambiguous state as a
  hard stop that asks the user what to do and performs no deletion.
- Require the branch tip to match the reviewed PR tip when PR-based cleanup is used.
- Revalidate every candidate immediately before removal.
- Do not provide a force-delete option for automated cleanup.
- Never claim to switch the active OpenCode session.

The safe cleanup proof is:

```text
managed path under source/
+ clean tracked, untracked, and ignored state
+ no local stash entries
+ configured remote exists and is reachable
+ upstream remote branch exists and is reachable
+ local branch is not ahead of upstream
+ cleanup target is not the main worktree
+ no conflicting worktree state
```

If any condition is false, preserve the worktree and report the exact reason.

### Command execution

Replace the limited `waiter.py` behavior with a reusable bounded command runner:

- Prefer argument arrays over shell strings.
- Provide explicit shell mode when shell syntax is required.
- Validate timeout and interval values.
- Capture bounded stdout and stderr.
- Return exit code, duration, timeout state, and last output.
- Support Windows and POSIX process behavior.

## Phase 2: Project Profiles and Startup

Startup is a toolkit concern. Agentic-repository startup commands must only route
to named technology-specific toolkit startup skills. They must not contain project
detection, command selection, process launching, or readiness logic.

## Project profile

Add an optional target-repository file:

```text
opencode.project.json
```

Explicit configuration has priority over detection.

Example:

```json
{
  "version": 1,
  "projectType": "react",
  "root": ".",
  "packageManager": "pnpm",
  "services": [
    {
      "id": "web",
      "cwd": ".",
      "command": ["pnpm", "dev"],
      "readiness": {
        "type": "http",
        "url": "http://127.0.0.1:3000",
        "timeoutSeconds": 60
      }
    }
  ],
  "checks": {
    "build": ["pnpm", "build"],
    "test": ["pnpm", "test"],
    "lint": ["pnpm", "lint"]
  }
}
```

The schema should support:

- Project type
- Repository and service roots
- Package manager/runtime
- Startup command as an argument array
- Environment variables
- Port/resource declarations
- Readiness checks
- Shutdown behavior
- Build, test, lint, and format commands
- Documentation roots

## Detection rules

Implement:

```text
.opencode/scripts/project_profile.py
.opencode/skills/toolkit-project-detection/
```

Detection must:

1. Read explicit `opencode.project.json` first.
2. Read the target repository's canonical startup instructions when present.
3. Scan known manifests and lockfiles.
4. Detect project type and package manager.
5. Detect candidate services and commands.
6. Report evidence for every detected value.
7. Produce a preview before execution.
8. Stop when candidates conflict or multiple roots are ambiguous.
9. Return “no applicable project type detected” instead of guessing.

Canonical target-repository startup guidance must be searched in this order:

1. `opencode.project.json`
2. `toolkit.startup.md` at the target repository root
3. An explicit `## Startup` section in the target repository's `AGENTS.md`
4. Technology-specific detection rules
5. Stop with an actionable missing-startup-instructions result

Only the first applicable source is used. General README prose is not treated as a
startup command unless it is explicitly referenced by one of these sources.

## Specialized skills

Add specialized toolkit skills with precise trigger descriptions and deterministic
rules:

```text
.opencode/skills/toolkit-startup-core/
.opencode/skills/toolkit-startup-react/
.opencode/skills/toolkit-startup-python/
.opencode/skills/toolkit-startup-dotnet/
.opencode/skills/toolkit-startup-node/
```

The skill names and descriptions must use the `toolkit.` namespace concept. They
must be loaded only for a selected target working repository, never as instructions
for changing the agentic repository.

### React / Node

- Respect explicit profile configuration.
- Detect package manager in this order: `pnpm-lock.yaml`, `yarn.lock`,
  `package-lock.json`, `bun.lock`.
- Detect framework from `package.json` dependencies.
- Select `dev` before `start` when no explicit command exists.
- Refuse when neither script exists.
- Never invent a port.
- Require selection when multiple frontend roots exist.

### Python

- Respect explicit profile configuration.
- Detect environment/package manager from `uv.lock`, `poetry.lock`,
  `Pipfile.lock`, `requirements.txt`, and `pyproject.toml`.
- Prefer declared project scripts.
- Recognize framework entrypoints only with explicit evidence.
- Require selection when multiple entrypoints exist.
- Refuse to guess between Flask, Django, FastAPI, or custom runners.

### C# / .NET

- Respect explicit profile configuration.
- Detect `.sln` and `.csproj` files.
- Use the only project automatically when exactly one exists.
- Require `--project` when multiple projects exist.
- Prefer `dotnet run --project <project>`.
- Use `launchSettings.json` only when explicitly selected.
- Use configured URL or health checks for readiness.

## Agentic startup command links

Create only thin agentic-repository command links:

```text
agentic_repo.startup.react  -> toolkit-startup-react
agentic_repo.startup.python -> toolkit-startup-python
agentic_repo.startup.dotnet -> toolkit-startup-dotnet
agentic_repo.startup.node   -> toolkit-startup-node
```

Each command body must only identify and load the named toolkit startup skill and
pass through the target context and arguments. It must not duplicate the skill's
technology rules or contain generic startup logic. Adding a new technology means
adding one new `agentic_repo.*` link and one new `toolkit-startup-*` skill.

## Startup process manager

Implement:

```text
.opencode/scripts/process_manager.py
```

The process manager is an implementation dependency of toolkit startup skills, not
an additional generic startup command. The agentic repository must expose only the
technology-specific startup links listed above.

The process manager must:

- Create a process record for every launch.
- Store PID, process group, command, cwd, environment summary, log paths, and
  timestamps.
- Support Windows and POSIX process groups.
- Detect port conflicts before launching.
- Support bounded readiness checks.
- Detect exited and orphaned processes.
- Stop recorded process groups.
- Never depend on an unavailable “separate terminal”.
- Never leave process ownership implicit.

The selected `toolkit-startup-*` skill owns the lifecycle operation and must expose
its own deterministic plan, run, status, and stop behavior internally. No generic
`/startup/*` command may bypass the technology-specific skill.

## Phase 3: Agent Redesign

Each agent must define:

- Purpose
- Required inputs
- Target resolution
- Allowed tools
- Forbidden actions
- Execution phases
- Confirmation points
- Completion criteria
- Output schema
- Failure behavior

Recommended roles:

```text
orchestrator
implementer
reviewer
startup
issue-manager
repository-manager
worktree-manager
sync
cluster
docs
frontend
backend
```

Do not define a repository-local `build` agent. OpenCode's built-in `build` agent
is the build agent for build commands.

### Permission rules

- Reviewer: read-only; may inspect Git diffs; cannot edit.
- Built-in OpenCode build agent: read-only verification by default; runs only
  explicitly selected existing checks.
- Implementer: may edit target working repositories; cannot commit, push, reset, or
  clean.
- Sync agent: commit, push, and PR operations require explicit confirmation.
- Repository manager: may register and list repositories; it must not delete a
  repository clone.
- Worktree manager: may remove only a proven-safe managed worktree; no force-delete
  path is available.
- Cluster agent: remote mutation requires command preview and approval.
- Startup agent: process launch and stop require an explicit target, selected
  toolkit startup skill, and lifecycle mode.
- Agentic-repository agents must not load toolkit instructions implicitly, and
  toolkit agents must not modify agentic-repository configuration unless explicitly
  authorized by an `agentic_repo.*` command.

Remove duplicated responsibilities between development review, review commands,
sync commands, and GitHub Issue skills.

## Phase 4: Command Redesign

### Development

Rewrite build, implementation, documentation, and review commands with exact check
selection and structured results. These are `toolkit.*` operations and must not be
loaded as instructions for modifying the agentic repository.

### Startup links

The agentic repository must contain only explicit technology links:

```text
agentic_repo.startup.react
agentic_repo.startup.python
agentic_repo.startup.dotnet
agentic_repo.startup.node
```

Each link loads exactly one matching `toolkit-startup-*` skill. There must be no
agentic-repository startup prompt containing generic frontend/backend detection,
command selection, process management, or readiness logic.

### GitHub Issues

Keep `github-issues` as the canonical Issue skill. Add:

- Exact repository precedence
- Issue body schema
- Project status semantics
- Deterministic branch naming
- Duplicate prevention
- Idempotent migration
- Preview before Issue/project mutation
- Explicit handling of partial failures

### GitHub management

Keep `github-management` for pull requests. Define:

- Exact PR resolution
- Complete paginated review-thread retrieval
- Classification criteria
- Reply/resolution confirmation
- Thread revalidation before mutation
- Stable per-thread action results

### Repository and worktree

Define exact arguments, source-slot allocation, path policies, branch behavior,
managed versus external repository handling, cleanup proof, and output records.

Repository removal is not an automation feature. The toolkit may register, list,
clone, and create worktrees, but it must not recursively delete a repository clone.
If the user deletes the agentic repository manually, only repositories physically
inside its gitignored `source/` directory are affected. External repositories are
never affected.

Document that creating a worktree does not switch the current OpenCode session.
Provide the supported way to open a new session in that path.

### Synchronization

Separate responsibilities into:

```text
sync/commit
sync/push
sync/pr
sync/ship
```

`ship` should orchestrate the other operations rather than duplicate them.
Each mutation must display a preview and require explicit authorization.

### Cluster

Define:

- Exact command representation
- Argument-array versus shell execution
- Remote-root containment
- Symlink behavior
- Timeout and cancellation
- Output capture
- Overwrite behavior
- Retry rules
- Destructive-command classification

## Phase 5: Templates, Schemas, and Documentation

Make templates machine-checkable. Required fields should include:

- Repository
- Branch
- Issue or PR number
- Changed files
- Commands executed
- Exit codes
- Test/build results
- Skipped checks and reasons
- Remaining limitations

Add validation for:

```text
issue-task.md
issue-analysis.md
summary.md
fix.md
fix-cr.md
pr-title.md
```

Update documentation to cover:

- Actual OpenCode command names
- Auto-discovery of commands, agents, and skills
- Explicit instruction registration
- Target repository selection
- Project profiles
- Startup lifecycle
- Supported runtimes
- Confirmation and safety rules
- Windows and Linux prerequisites

Review `.opencode/package.json` and document whether the plugin dependency is
required. Add supported Python, Node, GitHub CLI, and SSH versions where needed.

## Phase 6: Verification

Add tests for:

- JSON and Markdown frontmatter validation
- Target resolution precedence
- Registry path traversal
- Credential-bearing remotes
- Atomic registry updates
- Worktree collisions
- Dirty worktree protection
- Merged versus unmerged PR cleanup
- Project profile detection
- React, Python, and .NET startup planning
- Process lifecycle and readiness failures
- Timeout handling
- Windows and POSIX path behavior
- Command discovery
- Agent permissions
- Idempotent Issue migration

Initial local verification should use existing dependencies only:

```text
python -m compileall .opencode/scripts
python -m unittest discover
```

OpenCode smoke checks should verify:

- All expected commands are discovered
- All expected agents are discovered
- All expected skills are discovered
- `opencode.json` passes schema validation

End-to-end validation should cover:

1. External repository registration
2. Target resolution from the framework
3. Worktree creation and explicit session opening
4. Issue creation and migration reruns
5. Implementation workflow
6. Review workflow
7. Commit/push/PR confirmation boundaries
8. Merged, unmerged, dirty, detached, and reused worktrees
9. Frontend-only, backend-only, and multi-service startup
10. React, Python, .NET, monorepo, missing-dependency, and readiness-failure cases
11. Cluster upload, download, command, timeout, and overwrite behavior
12. Startup namespace links select the correct technology skill and do not contain
    duplicated startup logic.
13. Missing, unreachable, or unconfigured remotes prevent cleanup and produce a
    user decision request.
14. External repository paths are usable directly and are never deletion candidates.

## Recommended Implementation Order

1. Define contracts and safety policy.
2. Implement target resolution and state management.
3. Harden repository and worktree scripts.
4. Add project-profile schema and detection.
5. Add process management and startup lifecycle.
6. Rewrite and permission-harden agents.
7. Rewrite commands to consume the core contracts.
8. Strengthen templates and documentation.
9. Add tests and run the cross-platform verification matrix.
10. Verify namespace isolation and source-slot ownership before enabling any
    mutating workflow.

Do not rewrite prompts first. Without target resolution, project profiles, process
management, and script-level safety enforcement, improved prompts would still
leave behavior dependent on model interpretation.

## Acceptance Criteria

The plan is complete when:

- Every command has an explicit and testable contract.
- Every command has an explicit agent.
- Ambiguous repository targets fail closed.
- Mutating operations require preview and authorization.
- Startup works through profiles and deterministic adapters.
- React, Python, and .NET projects have separate specialized startup skills.
- Process startup, readiness, status, and shutdown are tracked.
- Repository and worktree operations are path-safe and never automatically delete
  repository clones.
- Managed worktrees are removed only after proving remote-commit completeness and
  local cleanliness.
- Missing or unreachable remotes always stop cleanup and ask the user what to do.
- Managed local repositories use `source/<repo_name>_slot<N>`; external repositories
  remain in their user-selected paths and are never deleted.
- `agentic_repo.*` and `toolkit.*` prompts, instructions, skills, and agents are
  completely separated.
- Startup commands in the agentic repository are only links to technology-specific
  toolkit startup skills; no generic startup command bypasses them.
- GitHub operations are idempotent where reruns are expected.
- Agents have least-privilege permissions and clear output contracts.
- Templates are validated.
- The repository has automated tests and documented supported environments.
