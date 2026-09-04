# Node Toolkit Startup Skill

## Overview

This skill provides deterministic startup and lifecycle management for Node.js projects.

## Prerequisites

- Node.js installed
- Package manager (npm, yarn, pnpm, or bun)

## Project Detection

### Automatic Detection
The skill automatically detects Node.js projects by looking for:
- `package.json` in the project root
- Node.js scripts in package.json scripts
- No React dependency (to distinguish from React projects)

### Explicit Configuration
Create `opencode.project.json` in the project root:

```json
{
  "version": 1,
  "projectType": "node",
  "root": ".",
  "packageManager": "npm",
  "services": [
    {
      "id": "api",
      "cwd": ".",
      "command": ["npm", "start"],
      "readiness": {
        "type": "http",
        "url": "http://127.0.0.1:8080",
        "timeoutSeconds": 30
      }
    }
  ],
  "checks": {
    "build": ["npm", "run", "build"],
    "test": ["npm", "test"],
    "lint": ["npm", "run", "lint"]
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
2. `start` script
3. `dev` script
4. Refuse if no usable script exists

## Commands

### Plan
Preview what will be done without executing:

```bash
# Preview startup plan
npm start --dry-run
```

### Run
Start the Node.js application:

```bash
# Using npm
npm start

# Using pnpm
pnpm start

# Using yarn
yarn start

# Using bun
bun run start
```

### Status
Check if the application is running:

```bash
# Check if process is running
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I "node.exe" > NUL
if %ERRORLEVEL% == 0 (
    echo Node process is running
) else (
    echo Node process is not running
)

# Check HTTP endpoint
curl -s http://127.0.0.1:8080 > /dev/null
if %ERRORLEVEL% == 0 (
    echo Server is responding
) else (
    echo Server is not responding
)
```

### Stop
Stop the application:

```bash
# Stop Node process
taskkill /IM node.exe /F

# Or use package manager script
npm stop
```

## Best Practices

1. **Use explicit configuration**: Always create `opencode.project.json` for production
2. **Use start for production**: Use `start` script for production applications
3. **Don't invent ports**: Use configured ports or detect from configuration
4. **Test frequently**: Run the application often to catch issues early

## Troubleshooting

### Port already in use
- Check if another process is using the port
- Kill the conflicting process
- Configure a different port in `opencode.project.json`

### Command not found
- Ensure package manager is installed
- Check if dependencies are installed
- Verify package.json scripts exist

### Application not responding
- Check if the application started successfully
- Verify the correct port is configured
- Check for errors in the console
