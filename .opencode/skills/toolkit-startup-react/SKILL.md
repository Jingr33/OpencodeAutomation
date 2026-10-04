# React Toolkit Startup Skill

## Overview

This skill provides deterministic startup and lifecycle management for React projects.

## Prerequisites

- Node.js installed
- Package manager (npm, yarn, pnpm, or bun)

## Project Detection

### Automatic Detection
The skill automatically detects React projects by looking for:
- `package.json` with React dependency
- `react` or `react-dom` in dependencies
- React scripts in package.json scripts

### Explicit Configuration
Create `opencode.project.json` in the project root:

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

## Package Manager Detection

The skill detects package managers in this order:
1. `pnpm-lock.yaml` → pnpm
2. `yarn.lock` → yarn
3. `package-lock.json` → npm
4. `bun.lock` → bun

## Command Selection

The skill selects commands in this order:
1. Explicit profile command
2. `dev` script (preferred over `start`)
3. `start` script
4. Refuse if no usable script exists

## Commands

### Plan
Preview what will be done without executing:

```bash
# Preview startup plan
pnpm dev --dry-run

# Or for npm
npm run dev --dry-run
```

### Run
Start the React development server:

```bash
# Using pnpm
pnpm dev

# Using npm
npm run dev

# Using yarn
yarn dev

# Using bun
bun run dev
```

### Status
Check if the development server is running:

```bash
# Check if process is running
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I "node.exe" > NUL
if %ERRORLEVEL% == 0 (
    echo Node process is running
) else (
    echo Node process is not running
)

# Check HTTP endpoint
curl -s http://127.0.0.1:3000 > /dev/null
if %ERRORLEVEL% == 0 (
    echo Server is responding
) else (
    echo Server is not responding
)
```

### Stop
Stop the development server:

```bash
# Stop Node process
taskkill /IM node.exe /F

# Or use package manager script
pnpm stop
```

## Best Practices

1. **Use explicit configuration**: Always create `opencode.project.json` for production
2. **Prefer dev over start**: Use `dev` script for development
3. **Don't invent ports**: Use configured ports or detect from configuration
4. **Test frequently**: Run the development server often to catch issues early

## Troubleshooting

### Port already in use
- Check if another process is using the port
- Kill the conflicting process
- Configure a different port in `opencode.project.json`

### Command not found
- Ensure package manager is installed
- Check if dependencies are installed
- Verify package.json scripts exist

### Server not responding
- Check if the server started successfully
- Verify the correct port is configured
- Check for build errors in the console
