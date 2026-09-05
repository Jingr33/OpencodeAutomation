# Namespace Separation: agentic_repo and toolkit

This document describes the separation between agentic-repository and toolkit namespaces.

## Overview

The OpenCode Automation framework uses two distinct namespaces:

1. **agentic_repo**: Commands, agents, and skills for operating the automation repository itself
2. **toolkit**: Commands, agents, and skills executed against target working repositories

## Namespace Structure

### agentic_repo Namespace

The `agentic_repo` namespace is reserved for commands that operate the agentic repository:

```
.opencode/
├── commands/
│   └── agentic_repo/
│       ├── agentic_repo.repository.*.md
│       ├── agentic_repo.worktree.*.md
│       └── agentic_repo.workspace.*.md
├── agents/
│   └── agentic_repo/
│       ├── agentic_repo.orchestrator.md
│       ├── agentic_repo.repository-manager.md
│       └── agentic_repo.worktree-manager.md
├── skills/
│   └── agentic_repo-*/
│       └── SKILL.md
└── instructions/
    └── agentic_repo/
        └── *.md
```

**agentic_repo Commands:**
- Repository registration and listing
- Worktree creation, listing, and removal
- Workspace management
- Framework configuration

### toolkit Namespace

The `toolkit` namespace is reserved for commands executed against target repositories:

```
.opencode/
├── commands/
│   └── toolkit/
│       ├── toolkit.implement.md
│       ├── toolkit.review.md
│       └── toolkit.startup.*.md
├── agents/
│   └── toolkit/
│       ├── toolkit.implementer.md
│       ├── toolkit.reviewer.md
│       └── toolkit.startup.md
├── skills/
│   └── toolkit-*/
│       └── SKILL.md
└── instructions/
    └── toolkit/
        └── *.md
```

**toolkit Commands:**
- Code implementation and review
- Build, test, and lint operations
- Technology-specific startup
- Project detection and profiling

## Directory Structure

```
.opencode/
├── commands/
│   ├── agentic_repo/           # agentic_repo commands
│   │   ├── agentic_repo.repository.register.md
│   │   ├── agentic_repo.repository.list.md
│   │   ├── agentic_repo.worktree.create.md
│   │   ├── agentic_repo.worktree.list.md
│   │   ├── agentic_repo.worktree.remove.md
│   │   ├── agentic_repo.worktree.cleanup.md
│   │   ├── agentic_repo.workspace.add.md
│   │   ├── agentic_repo.workspace.list.md
│   │   └── agentic_repo.workspace.remove.md
│   └── toolkit/                # toolkit commands
│       ├── toolkit.implement.md
│       ├── toolkit.review.md
│       ├── toolkit.startup.react.md
│       ├── toolkit.startup.python.md
│       ├── toolkit.startup.dotnet.md
│       └── toolkit.startup.node.md
├── agents/
│   ├── agentic_repo/           # agentic_repo agents
│   │   ├── agentic_repo.orchestrator.md
│   │   ├── agentic_repo.repository-manager.md
│   │   └── agentic_repo.worktree-manager.md
│   └── toolkit/                # toolkit agents
│       ├── toolkit.implementer.md
│       ├── toolkit.reviewer.md
│       └── toolkit.startup.md
├── skills/
│   ├── agentic_repo-worktree/  # agentic_repo skills
│   │   └── SKILL.md
│   ├── agentic_repo-repository/
│   │   └── SKILL.md
│   ├── toolkit-startup-react/  # toolkit skills
│   │   └── SKILL.md
│   ├── toolkit-startup-python/
│   │   └── SKILL.md
│   └── toolkit-startup-dotnet/
│       └── SKILL.md
└── instructions/
    ├── agentic_repo/           # agentic_repo instructions
    │   └── *.md
    └── toolkit/                # toolkit instructions
        └── *.md
```

## Configuration

### opencode.json

The `opencode.json` file loads only agentic-repository instructions:

```json
{
  "instructions": [
    ".opencode/instructions/agentic_repo/general.md",
    ".opencode/instructions/agentic_repo/coding-standards.md",
    ".opencode/instructions/agentic_repo/github.md",
    ".opencode/instructions/agentic_repo/worktrees.md"
  ]
}
```

### Target Repository Configuration

Toolkit instructions, skills, and agents are loaded explicitly for a selected target repository:

```bash
# Load toolkit instructions for a specific target
python .opencode/scripts/context.py --repo /path/to/target
```

## Rules

1. **agentic_repo agents MUST NOT load toolkit instructions implicitly**
2. **toolkit agents MUST NOT modify agentic-repository configuration** unless explicitly authorized
3. **No unprefixed shared prompt may be loaded implicitly**
4. **Any bridge from agentic_repo.* startup command to a toolkit.* skill must be explicit**

## Migration Path

To migrate existing commands to the new namespace structure:

1. Create the new directory structure
2. Move commands to the appropriate namespace
3. Update command names and references
4. Test that commands work correctly
5. Update documentation

## Examples

### agentic_repo Command Example

```yaml
---
description: Create an isolated worktree and branch for a task
subtask: true
---

Load the `agentic_repo-worktree` skill. Parse `$ARGUMENTS` as `<branch> [base]`, with optional
`--repo <path>` and `--path <path>`. Run:

```bash
python .opencode/scripts/worktree.py create <branch> [base] [--repo <path>] [--path <path>]
```
```

### toolkit Command Example

```yaml
---
description: Implement features in the target repository
subtask: true
---

Load the `toolkit-implementer` agent. Parse `$ARGUMENTS` as the feature description.
Resolve the target repository using the context resolver.
Implement the feature following the target repository's conventions.
```
