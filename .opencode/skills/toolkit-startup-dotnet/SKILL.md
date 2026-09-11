# .NET Toolkit Startup Skill

## Overview

This skill provides deterministic startup and lifecycle management for C# and .NET projects.

## Prerequisites

- .NET SDK 6.0+ installed
- `dotnet` command available in PATH

## Project Detection

### Automatic Detection
The skill automatically detects .NET projects by looking for:
- `.sln` solution files
- `.csproj` project files
- `launchSettings.json` configuration
- C# files (`.cs`) in the project

### Explicit Configuration
Create `opencode.project.json` in the project root:

```json
{
  "version": 1,
  "projectType": "dotnet",
  "root": ".",
  "packageManager": "dotnet",
  "services": [
    {
      "id": "api",
      "cwd": "./src/MyApi",
      "command": ["dotnet", "run", "--project", "MyApi.csproj"],
      "readiness": {
        "type": "http",
        "url": "http://127.0.0.1:5000",
        "timeoutSeconds": 30
      }
    }
  ],
  "checks": {
    "build": ["dotnet", "build"],
    "test": ["dotnet", "test"],
    "lint": ["dotnet", "format", "--verify-no-changes"]
  }
}
```

## Project Resolution

### Single Project
When exactly one `.csproj` file exists, use it automatically.

### Multiple Projects
When multiple `.csproj` files exist:
1. Check for solution file (`.sln`)
2. Require `--project` argument or profile configuration
3. Refuse to guess between projects

### Solution File
If a `.sln` file exists:
1. Parse solution to find projects
2. Use the only project if exactly one exists
3. Require selection if multiple projects exist

## Commands

### Plan
Preview what will be done without executing:

```bash
# Preview startup plan
dotnet run --project MyApi.csproj --dry-run
```

### Run
Start the .NET application:

```bash
# Using dotnet run
dotnet run --project MyApi.csproj

# Using dotnet run with specific configuration
dotnet run --project MyApi.csproj --configuration Release

# Using dotnet run with launch profile
dotnet run --project MyApi.csproj --launch-profile "Development"
```

### Status
Check if the application is running:

```bash
# Check if dotnet process is running
tasklist /FI "IMAGENAME eq dotnet.exe" 2>NUL | find /I "dotnet.exe" > NUL
if %ERRORLEVEL% == 0 (
    echo .NET process is running
) else (
    echo .NET process is not running
)

# Check HTTP endpoint
curl -s http://127.0.0.1:5000 > /dev/null
if %ERRORLEVEL% == 0 (
    echo Server is responding
) else (
    echo Server is not responding
)
```

### Stop
Stop the application:

```bash
# Stop dotnet process
taskkill /IM dotnet.exe /F
```

## Launch Profiles

The skill uses `launchSettings.json` only when explicitly selected:

```json
{
  "profiles": {
    "MyApi": {
      "commandName": "Project",
      "dotnetRunMessages": true,
      "launchBrowser": false,
      "applicationUrl": "http://127.0.0.1:5000",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      }
    }
  }
}
```

## Best Practices

1. **Use explicit configuration**: Always create `opencode.project.json` for production
2. **Prefer dotnet run**: Use `dotnet run --project` for development
3. **Specify project**: Use `--project` when multiple projects exist
4. **Don't use launchSettings**: Only use when explicitly selected
5. **Test frequently**: Run the application often to catch issues early

## Troubleshooting

### Port already in use
- Check if another process is using the port
- Kill the conflicting process
- Configure a different port in `opencode.project.json`

### Project not found
- Ensure `.csproj` file exists
- Check project name spelling
- Verify path is correct

### Build failed
- Check for compilation errors
- Verify NuGet packages are restored
- Ensure correct .NET SDK version

### Application not responding
- Check if the application started successfully
- Verify the correct port is configured
- Check for exceptions in the console
- Ensure database or other services are running
