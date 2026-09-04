# Development and Startup Command Contracts

This document defines the contracts for development, implementation, documentation, review, build, and startup commands.

## Command Contracts

### Implement Command

**Syntax:**
```
implement <description> [--repo <path>] [--dry-run] [--apply]
```

**Arguments:**
- `description`: Feature or task description
- `--repo`: Target repository path (required for toolkit commands)
- `--dry-run`: Preview changes without applying
- `--apply`: Authorize and apply changes

**Preconditions:**
- Target repository must be specified and accessible
- Working directory must be clean
- Required dependencies must be installed

**Side Effects:**
- Creates or modifies files in target repository
- May create new branches

**Outputs:**
- Changed files list
- Verification results
- Summary of changes

**Confirmation:**
- Required for file modifications
- Preview must be shown before applying

### Review Command

**Syntax:**
```
review [--repo <path>] [--format <text|json>]
```

**Arguments:**
- `--repo`: Target repository path
- `--format`: Output format (default: text)

**Preconditions:**
- Target repository must be specified
- Code changes must exist

**Side Effects:**
- None (read-only operation)

**Outputs:**
- Review findings
- Suggestions
- Approval status

**Confirmation:**
- Not required (read-only)

### Build Command

**Syntax:**
```
build [--repo <path>] [--project <name>] [--configuration <Debug|Release>]
```

**Arguments:**
- `--repo`: Target repository path
- `--project`: Project name (required for .NET)
- `--configuration`: Build configuration (default: Debug)

**Preconditions:**
- Target repository must be specified
- Project must be buildable
- Required SDK/tools must be installed

**Side Effects:**
- Creates build artifacts
- May modify build directories

**Outputs:**
- Build result
- Error messages
- Build duration

**Confirmation:**
- Not required (standard build)

### Test Command

**Syntax:**
```
test [--repo <path>] [--filter <expression>] [--logger <logger>]
```

**Arguments:**
- `--repo`: Target repository path
- `--filter`: Test filter expression
- `--logger`: Test logger

**Preconditions:**
- Target repository must be specified
- Tests must exist
- Test framework must be installed

**Side Effects:**
- May create test results
- May modify test output directories

**Outputs:**
- Test results
- Pass/fail counts
- Test duration

**Confirmation:**
- Not required (standard test)

### Lint Command

**Syntax:**
```
lint [--repo <path>] [--fix] [--format <format>]
```

**Arguments:**
- `--repo`: Target repository path
- `--fix`: Auto-fix issues
- `--format`: Output format

**Preconditions:**
- Target repository must be specified
- Linter must be installed

**Side Effects:**
- May modify files when `--fix` is used

**Outputs:**
- Lint findings
- Fixed files (when `--fix` is used)

**Confirmation:**
- Required when `--fix` is used

## Startup Commands

### Startup Commands Must Be Thin Links

Startup commands in the agentic repository must only route to named technology-specific toolkit startup skills. They must not contain:
- Generic startup detection
- Command selection logic
- Process launching
- Readiness checking

### Startup Link Commands

```
agentic_repo.startup.react  -> toolkit-startup-react
agentic_repo.startup.python -> toolkit-startup-python
agentic_repo.startup.dotnet -> toolkit-startup-dotnet
agentic_repo.startup.node   -> toolkit-startup-node
agentic_repo.startup.godot  -> toolkit-startup-godot
```

Each link must:
1. Identify the target repository
2. Load the named toolkit startup skill
3. Pass through arguments and configuration
4. Return structured results

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

Checks must be selected deterministically:

1. Explicit profile configuration
2. Package.json scripts (for Node.js/React)
3. pyproject.toml scripts (for Python)
4. .csproj build targets (for .NET)
5. Refuse if no checks available

### Skipped Checks

When a check is skipped, report:
- Check name
- Reason for skipping
- Alternative check (if available)

## Target Resolution

### Explicit Target Selection

Commands must use explicit target selection:
- `--repo` argument
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
