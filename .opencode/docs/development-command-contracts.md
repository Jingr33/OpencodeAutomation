# Development and Startup Command Contracts

This document defines the contracts for development, implementation, documentation, review, build, and startup commands.

## Command Contracts

### Implement Command

**Syntax:**
```
implement <issue-number>
```

**Arguments:**
- `issue-number`: GitHub Issue number to implement

**Preconditions:**
- Issue must exist and be in `Ready` or `Backlog` status
- Target repository must be accessible
- Working directory must be clean (no uncommitted changes)
- Required dependencies must be installed

**Side Effects:**
- Creates or modifies files in target repository
- Creates a dedicated branch and worktree
- Updates GitHub Project status to `In progress`

**Outputs:**
- Changed files list
- Verification results
- Summary posted as Issue comment

**Confirmation:**
- Required for file modifications
- Preview must be shown before applying

### Build Command

**Syntax:**
```
build
```

**Arguments:**
- None (operates on active repository)

**Preconditions:**
- Target repository must be accessible
- Repository must have buildable content

**Side Effects:**
- Runs dependency, compile, test, and lint checks
- May create build artifacts

**Outputs:**
- Check results (pass/fail)
- Error messages
- Command output

**Confirmation:**
- Not required (standard build)

### CR (Code Review) Command

**Syntax:**
```
cr
```

**Arguments:**
- None (operates on staged and unstaged changes)

**Preconditions:**
- Code changes must exist (staged or unstaged)

**Side Effects:**
- None (read-only operation)

**Outputs:**
- Socratic review questions
- Hints escalating to direct questions

**Confirmation:**
- Not required (read-only)

### Document Command

**Syntax:**
```
document <target>
```

**Arguments:**
- `target`: What to document (`opencode` for shared setup, `all` for stale pages, or specific topic)

**Preconditions:**
- Target repository must be accessible
- Existing documentation structure must be inspected first

**Side Effects:**
- May create or update documentation files

**Outputs:**
- Documentation changes
- Summary of updates

**Confirmation:**
- Required for file modifications

## Startup Commands

### Startup Commands Must Be Thin Links

Startup commands in the agentic repository must only route to named technology-specific toolkit startup skills. They must not contain:
- Generic startup detection
- Command selection logic
- Process launching
- Readiness checking

### Available Startup Commands

```
startup/all      -> Start all documented development processes
startup/backend  -> Start backend or service process
startup/frontend -> Start frontend development process
```

Each startup command must:
1. Inspect the repository's README, package manifests, and development scripts
2. Detect the appropriate entrypoint and documented command
3. Report the command before running it if multiple candidates exist
4. Never invent framework-specific flags or ports

### Technology Skill Contract

Each technology startup skill must provide:

**Plan:**
- Preview startup command
- Show configuration
- Display readiness checks

**Run:**
- Start the application
- Track process ID
- Monitor readiness

**Status:**
- Show process status
- Check readiness
- Display logs

**Stop:**
- Stop the process
- Clean up resources
- Report status

## Check Selection

### Deterministic Check Selection

Checks must be selected deterministically based on the repository's actual configuration:

1. Explicit profile configuration
2. Package.json scripts (for Node.js/React)
3. pyproject.toml scripts (for Python)
4. Makefile targets
5. Refuse if no checks available

### Skipped Checks

When a check is skipped, report:
- Check name
- Reason for skipping
- Alternative check (if available)

## Target Resolution

### Explicit Target Selection

Commands must use explicit target selection:
- `--repo` argument (where supported)
- `OPENCODE_TARGET_REPO` environment variable
- Current checkout (only if not agentic repository)

### Fail Closed on Ambiguity

When target is ambiguous:
- Return error with clear message
- Require explicit target specification
- Do not guess or use defaults

## Confirmation Boundaries

### Mutations Requiring Confirmation

- File modifications
- Branch creation
- Commit creation
- Push operations
- PR creation
- Process startup
- Process shutdown

### Read-Only Operations

- File inspection
- Git status
- Code review
- Documentation generation
- Test execution (standard)
- Build execution (standard)

## Output Format

### Structured Results

All commands must return structured results:

```json
{
  "command": "implement",
  "status": "succeeded",
  "target": "/path/to/repository",
  "changes": ["file1.cs", "file2.cs"],
  "verification": {
    "passed": true,
    "tests": "10/10",
    "build": "success"
  },
  "summary": "Implemented feature X"
}
```

### Error Format

Errors must be structured:

```json
{
  "command": "implement",
  "status": "failed",
  "error": {
    "code": "target_required",
    "message": "Target repository is required",
    "action": "Specify --repo or OPENCODE_TARGET_REPO"
  }
}
```
