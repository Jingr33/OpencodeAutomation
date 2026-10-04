# Agent Redesign and Permission Boundaries

This document defines the existing agents with explicit permissions and
boundaries derived from the actual agent files in `.opencode/agents`.

## Agent Roles

### Dev (Development Agent)
**Purpose**: Implements a GitHub Issue or local task in the active repository
**Inputs**: Task specification, active repository
**Target Resolution**: Detects repository architecture and conventions from the
checkout itself
**Tools**: File editing, Bash, glob, grep, read, question
**Forbidden Actions**: No restrictions beyond repository-specific conventions
**Phases**: Inspect, plan, implement, verify, report
**Completion Criteria**: Task implemented and verified
**Output Schema**: Changed files, verification results, summary

### CR (Code Review Agent)
**Purpose**: Reviews changes using escalating questions and no suggested
solutions
**Inputs**: Requested diff, review criteria
**Target Resolution**: Must have explicit diff or branch to review
**Tools**: Read-only file access, glob, grep
**Forbidden Actions**: Cannot edit files, cannot run Bash; questions only
**Phases**: Analyze, question, escalate, report
**Completion Criteria**: Review completed with actionable feedback
**Output Schema**: Review findings, suggestions, approval status

### Sync (Synchronization Agent)
**Purpose**: Synchronizes the active repository, commits, pushes, and creates
pull requests
**Inputs**: Changes, repository, synchronization type
**Target Resolution**: Inspects active repository, remote, branch, and issue
association before acting
**Tools**: Bash, glob, grep, read, question
**Forbidden Actions**: No webfetch; asks before force-pushing, rewriting
history, or committing unrelated changes
**Phases**: Commit, push, PR, ship
**Completion Criteria**: Synchronization completed successfully
**Output Schema**: Commit hash, PR URL, status

### Cluster (Remote Cluster Agent)
**Purpose**: Runs explicitly requested file transfers and commands on a
configured remote host
**Inputs**: Command, remote host, configuration
**Target Resolution**: Uses `OPENCODE_CLUSTER_*` environment configuration
**Tools**: Bash, glob, grep, read, skill, question
**Forbidden Actions**: Cannot edit local files; remote mutations require
explicit confirmation
**Phases**: Connect, execute, verify, disconnect
**Completion Criteria**: Command executed successfully
**Output Schema**: Command output, exit code, status

### Docs (Documentation Agent)
**Purpose**: Creates and maintains documentation for the active repository and
OpenCode setup
**Inputs**: Documentation requirements, target repository
**Target Resolution**: Inspects repository documentation structure before
editing
**Tools**: File editing, Bash, glob, grep, read
**Forbidden Actions**: No webfetch; documentation only
**Phases**: Analyze, generate, verify, report
**Completion Criteria**: Documentation generated and verified
**Output Schema**: Documentation files, summary

### Frontend (Frontend Specialist)
**Purpose**: Frontend implementation specialist for the active repository
**Inputs**: Frontend requirements, target repository
**Target Resolution**: Detects active frontend framework and tooling from
repository
**Tools**: File editing, Bash, glob, grep, read
**Forbidden Actions**: Follows existing conventions; does not assume React,
Vite, or Material UI unless the repository uses them
**Phases**: Analyze, implement, verify, report
**Completion Criteria**: Frontend changes implemented and verified
**Output Schema**: Changed files, verification results, summary

### Backend (Backend Specialist)
**Purpose**: Backend and service implementation specialist for the active
repository
**Inputs**: Backend requirements, target repository
**Target Resolution**: Identifies backend boundaries from package manifests,
service folders, or API entrypoints
**Tools**: File editing, Bash, glob, grep, read
**Forbidden Actions**: Follows local conventions; does not impose a specific
framework or directory name
**Phases**: Analyze, implement, verify, report
**Completion Criteria**: Backend changes implemented and verified
**Output Schema**: Changed files, verification results, summary

## Permission Rules

### Read-Only Operations
- CR agent: Can inspect files and diffs, cannot edit or run Bash
- All agents: Read is always allowed

### Mutations with Confirmation
- Sync operations: Commit, push, PR require explicit confirmation
- Cluster operations: Remote mutations require approval
- Dev agent: Detects conventions before editing; keeps changes minimal

### Forbidden Operations
- CR agent: Cannot edit files or run Bash; questions only
- Cluster agent: Cannot edit local files
- Docs agent: No webfetch access
- Sync agent: No webfetch access

## Namespace Isolation

### Repository Agents
- Dev, CR, Frontend, Backend: Operate against the active checkout
- Docs: Operates on the active repository and `.opencode` configuration

### Operations Agents
- Sync: Manages commit, push, and PR workflow for the active checkout
- Cluster: Executes remote operations using configured host settings

## Implementation Notes

1. **Least Privilege**: Each agent has only the tools required for its purpose
2. **Explicit Authorization**: Mutations require explicit confirmation
3. **Convention Detection**: Frontend and backend agents detect frameworks from
   the repository rather than assuming defaults
4. **Safety Checks**: Destructive operations require validation
5. **Verification**: All operations verify completion before reporting success
