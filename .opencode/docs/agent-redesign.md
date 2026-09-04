# Agent Redesign and Permission Boundaries

This document defines the redesigned agents with explicit permissions and boundaries.

## Agent Roles

### Orchestrator
**Purpose**: Coordinate multiple agents and manage workflow execution
**Inputs**: Task description, agent list, workflow configuration
**Target Resolution**: Uses context resolver to determine target repository
**Tools**: Read-only access to all resources
**Forbidden Actions**: Cannot modify code, create commits, or push changes
**Phases**: Plan, coordinate, verify, report
**Completion Criteria**: All sub-agents complete successfully
**Output Schema**: Workflow status, agent results, summary

### Implementer
**Purpose**: Implement code changes in target repositories
**Inputs**: Task description, target repository, code specifications
**Target Resolution**: Must have explicit target repository
**Tools**: File editing, code generation
**Forbidden Actions**: Cannot commit, push, reset, or clean; cannot modify agentic repository
**Phases**: Analyze, implement, verify, report
**Completion Criteria**: Code changes implemented and verified
**Output Schema**: Changed files, verification results, summary

### Reviewer
**Purpose**: Review code changes and provide feedback
**Inputs**: Code changes, review criteria
**Target Resolution**: Must have explicit target repository
**Tools**: Read-only file access, Git diff inspection
**Forbidden Actions**: Cannot edit files, cannot modify code; read-only by default
**Phases**: Analyze, review, report
**Completion Criteria**: Review completed with actionable feedback
**Output Schema**: Review findings, suggestions, approval status

### Startup
**Purpose**: Manage application startup and lifecycle
**Inputs**: Target repository, startup configuration
**Target Resolution**: Must have explicit target repository
**Tools**: Process management, port checking
**Forbidden Actions**: Cannot modify code; lifecycle orchestration only
**Phases**: Detect, plan, start, verify, status, stop
**Completion Criteria**: Application started and ready
**Output Schema**: Process status, readiness, logs

### Issue Manager
**Purpose**: Create and manage GitHub Issues
**Inputs**: Issue details, repository
**Target Resolution**: Repository from context or explicit argument
**Tools**: GitHub API, file creation
**Forbidden Actions**: Cannot implement code; Issue lifecycle only
**Phases**: Create, update, close, migrate
**Completion Criteria**: Issue created/updated successfully
**Output Schema**: Issue URL, status, comments

### Repository Manager
**Purpose**: Register and manage repositories
**Inputs**: Repository URL, configuration
**Target Resolution**: Repository registration
**Tools**: Git operations, file system
**Forbidden Actions**: Cannot delete repository clones; registration only
**Phases**: Register, list, verify
**Completion Criteria**: Repository registered successfully
**Output Schema**: Repository path, status, configuration

### Worktree Manager
**Purpose**: Create and manage Git worktrees
**Inputs**: Branch name, repository
**Target Resolution**: Repository from context
**Tools**: Git worktree operations
**Forbidden Actions**: Cannot force-delete; safety checks required
**Phases**: Create, list, remove, cleanup
**Completion Criteria**: Worktree created/removed successfully
**Output Schema**: Worktree path, branch, status

### Sync Agent
**Purpose**: Synchronize code changes (commit, push, PR)
**Inputs**: Changes, repository, synchronization type
**Target Resolution**: Must have explicit target repository
**Tools**: Git operations, GitHub API
**Forbidden Actions**: Requires explicit confirmation for mutations
**Phases**: Commit, push, PR, ship
**Completion Criteria**: Synchronization completed successfully
**Output Schema**: Commit hash, PR URL, status

### Cluster Agent
**Purpose**: Execute commands on remote systems
**Inputs**: Command, remote host, configuration
**Target Resolution**: Remote host configuration
**Tools**: SSH, SCP
**Forbidden Actions**: Remote mutations require approval
**Phases**: Connect, execute, verify, disconnect
**Completion Criteria**: Command executed successfully
**Output Schema**: Command output, exit code, status

### Docs Agent
**Purpose**: Generate and maintain documentation
**Inputs**: Documentation requirements, target repository
**Target Resolution**: Must have explicit target repository
**Tools**: File creation, markdown generation
**Forbidden Actions**: Cannot modify code; documentation only
**Phases**: Analyze, generate, verify, report
**Completion Criteria**: Documentation generated and verified
**Output Schema**: Documentation files, summary

### Frontend Agent
**Purpose**: Handle frontend-specific development tasks
**Inputs**: Frontend requirements, target repository
**Target Resolution**: Must have explicit target repository
**Tools**: File editing, package management
**Forbidden Actions**: Cannot commit, push, or modify backend code
**Phases**: Analyze, implement, verify, report
**Completion Criteria**: Frontend changes implemented and verified
**Output Schema**: Changed files, verification results, summary

### Backend Agent
**Purpose**: Handle backend-specific development tasks
**Inputs**: Backend requirements, target repository
**Target Resolution**: Must have explicit target repository
**Tools**: File editing, database operations
**Forbidden Actions**: Cannot commit, push, or modify frontend code
**Phases**: Analyze, implement, verify, report
**Completion Criteria**: Backend changes implemented and verified
**Output Schema**: Changed files, verification results, summary

## Permission Rules

### Read-Only Operations
- Reviewer: Can inspect files and Git diffs, cannot edit
- Documentation agent: Can read code, cannot modify
- Analysis operations: Can read state, cannot modify

### Mutations with Confirmation
- Sync operations: Commit, push, PR require explicit confirmation
- Cluster operations: Remote mutations require approval
- Worktree operations: Creation/removal require confirmation

### Forbidden Operations
- Implementer: Cannot commit, push, reset, or clean
- Repository Manager: Cannot delete repository clones
- Worktree Manager: Cannot force-delete without safety checks
- All agents: Cannot cross-modify namespaces implicitly

## Namespace Isolation

### agentic_repo Namespace
- Commands operate on the automation repository itself
- Agents: orchestrator, repository-manager, worktree-manager
- Skills: worktree, repository, workspace
- Instructions: agentic_repo-specific

### toolkit Namespace
- Commands execute against target working repositories
- Agents: implementer, reviewer, startup, docs, frontend, backend
- Skills: toolkit-startup-*, toolkit-implement, toolkit-review
- Instructions: toolkit-specific

## Implementation Notes

1. **Least Privilege**: Each agent has only the tools required for its purpose
2. **Explicit Authorization**: Mutations require explicit confirmation
3. **Namespace Isolation**: agentic_repo and toolkit agents cannot cross-modify
4. **Safety Checks**: Destructive operations require validation
5. **Verification**: All operations verify completion before reporting success
