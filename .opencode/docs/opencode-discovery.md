# OpenCode Discovery and Command Metadata

This document describes how OpenCode discovers commands, agents, and skills in this repository.

## Discovery Behavior

OpenCode automatically discovers commands, agents, and skills from the `.opencode/` directory structure.

### Commands

Commands are discovered from `.opencode/commands/` directory. Each command is a Markdown file with YAML frontmatter.

**Directory Structure:**
```
.opencode/commands/
├── cluster/
│   └── scp.md
├── dev/
│   ├── implement.md
│   ├── review.md
│   └── startup/
│       └── ...
├── issue/
│   ├── analyze.md
│   ├── create.md
│   ├── fix.md
│   └── migrate.md
├── repo/
│   └── ...
├── review/
│   ├── cr.md
│   └── fix-cr.md
├── sync/
│   ├── pull.md
│   ├── push.md
│   └── ship.md
└── worktree/
    ├── cleanup.md
    ├── create.md
    ├── list.md
    └── remove.md
```

**Command Naming:**
- Commands are named by their path relative to `.opencode/commands/`
- Example: `.opencode/commands/dev/implement.md` → `dev/implement`
- Example: `.opencode/commands/worktree/create.md` → `worktree/create`

**Command Frontmatter:**
```yaml
---
description: Command description
subtask: true
---
```

### Agents

Agents are discovered from `.opencode/agents/` directory. Each agent is a Markdown file.

**Directory Structure:**
```
.opencode/agents/
├── orchestrator.md
├── implementer.md
├── reviewer.md
└── ...
```

### Skills

Skills are discovered from `.opencode/skills/` directory. Each skill is a directory with a `SKILL.md` file.

**Directory Structure:**
```
.opencode/skills/
├── worktree/
│   └── SKILL.md
├── github-issues/
│   └── SKILL.md
├── analyze/
│   └── SKILL.md
└── ...
```

**Skill Naming:**
- Skills are named by their directory name
- Example: `.opencode/skills/worktree/SKILL.md` → `worktree`
- Example: `.opencode/skills/github-issues/SKILL.md` → `github-issues`

## Instructions

Instructions are loaded from files specified in `opencode.json`:

```json
{
  "instructions": [
    ".opencode/instructions/general.md",
    ".opencode/instructions/coding-standards.md",
    ".opencode/instructions/github.md",
    ".opencode/instructions/worktrees.md"
  ]
}
```

## Agent Assignment

Every command MUST have an explicit agent assigned. The agent is specified in the command's YAML frontmatter or in the command definition.

**Current Agent Assignments:**

| Command | Agent | Description |
|---------|-------|-------------|
| `cluster/scp` | cluster-manager | Transfer files via SCP |
| `dev/implement` | implementer | Implement features |
| `dev/review` | reviewer | Review code changes |
| `dev/startup/*` | startup-manager | Toolkit startup commands |
| `issue/analyze` | issue-manager | Analyze issues |
| `issue/create` | issue-manager | Create issues |
| `issue/fix` | implementer | Fix issues |
| `issue/migrate` | issue-manager | Migrate issues |
| `repo/*` | repository-manager | Repository management |
| `review/cr` | reviewer | Code review |
| `review/fix-cr` | implementer | Fix code review comments |
| `sync/pull` | sync | Pull changes |
| `sync/push` | sync | Push changes |
| `sync/ship` | sync | Ship changes |
| `worktree/cleanup` | worktree-manager | Cleanup worktrees |
| `worktree/create` | worktree-manager | Create worktrees |
| `worktree/list` | worktree-manager | List worktrees |
| `worktree/remove` | worktree-manager | Remove worktrees |

## Verification Commands

To verify discovery behavior:

```bash
# List all commands
ls -la .opencode/commands/

# List all agents
ls -la .opencode/agents/

# List all skills
ls -la .opencode/skills/

# Verify command frontmatter
grep -r "^---" .opencode/commands/
```

## Common Issues

### Commands not discovered
- Ensure the command file has proper YAML frontmatter
- Check the file extension is `.md`
- Verify the file is in the correct directory

### Agents not discovered
- Ensure the agent file exists in `.opencode/agents/`
- Check the file has proper content

### Skills not discovered
- Ensure the skill directory exists in `.opencode/skills/`
- Check the `SKILL.md` file exists in the directory

## Best Practices

1. **Use descriptive names**: Command and skill names should be clear and descriptive
2. **Consistent structure**: Follow the established directory structure
3. **Explicit agent assignment**: Always assign an agent to commands
4. **Documentation**: Include clear descriptions in frontmatter
5. **Testing**: Verify commands work as expected after creation
