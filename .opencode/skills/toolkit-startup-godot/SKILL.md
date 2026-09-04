# GODOT Toolkit Startup Skill

## Overview

This skill provides deterministic startup and lifecycle management for GODOT game development projects. It supports two integration modes:

1. **GODOT MCP Mode**: Full control over the game through GODOT's Multiplayer Control Protocol
2. **Editor Mode**: OpenCode as a text file editor only (safer but more limited)

## Prerequisites

- GODOT Engine installed and accessible via PATH
- GODOT project file (`project.godot`) in the project root
- For MCP mode: GODOT MCP server running

## Project Detection

### Automatic Detection
The skill automatically detects GODOT projects by looking for:
- `project.godot` file in the project root
- `.godot` directory (GODOT project cache)
- GDScript files (`.gd`)
- Scene files (`.tscn`, `.tres`)

### Explicit Configuration
Create `opencode.project.json` in the project root:

```json
{
  "version": 1,
  "projectType": "godot",
  "root": ".",
  "godot": {
    "version": "4.2",
    "mode": "mcp",
    "mcpPort": 6006,
    "scene": "res://main.tscn"
  },
  "services": [
    {
      "id": "godot",
      "cwd": ".",
      "command": ["godot", "--path", ".", "--remote-debug", "tcp://127.0.0.1:6006"],
      "readiness": {
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 6006,
        "timeoutSeconds": 30
      }
    }
  ],
  "checks": {
    "build": ["godot", "--headless", "--export-release", "Linux/X11"],
    "test": ["godot", "--headless", "--script", "res://test_runner.gd"]
  }
}
```

## Integration Modes

### Mode 1: GODOT MCP (Full Control)

**Pros:**
- Full control over the game
- Real-time debugging capabilities
- Scene inspection and manipulation
- Script execution and testing

**Cons:**
- More complex setup
- Requires MCP server running
- Higher risk of breaking game state

**Setup:**
1. Install GODOT MCP server
2. Start GODOT with MCP enabled
3. Configure OpenCode to connect to MCP

### Mode 2: Editor Mode (Safe)

**Pros:**
- Safer - only edits code files
- No risk of breaking game state
- Simpler setup
- Works without MCP

**Cons:**
- Limited to code editing only
- No real-time debugging
- Cannot inspect game state

**Setup:**
1. Open project folder in OpenCode
2. Edit GDScript files directly
3. Run game separately to test changes

## Commands

### Plan
Preview what will be done without executing:

```bash
# Preview startup plan
godot --path . --headless --quit

# Preview export plan
godot --path . --headless --export-release Linux/X11
```

### Run
Start the GODOT project:

```bash
# Run with MCP (if configured)
godot --path . --remote-debug tcp://127.0.0.1:6006

# Run in editor mode
godot --path .
```

### Status
Check if GODOT is running:

```bash
# Check if GODOT process is running
tasklist /FI "IMAGENAME eq godot.exe" 2>NUL | find /I "godot.exe" > NUL
if %ERRORLEVEL% == 0 (
    echo GODOT is running
) else (
    echo GODOT is not running
)
```

### Stop
Stop the GODOT project:

```bash
# Stop GODOT process
taskkill /IM godot.exe /F
```

## Development Workflow

### 1. Project Setup
```bash
# Create new GODOT project
godot --headless --create-project .
```

### 2. Scene Management
```bash
# Open specific scene
godot --path . --scene res://main.tscn
```

### 3. Script Development
```bash
# Run specific script
godot --headless --script res://scripts/player.gd
```

### 4. Export
```bash
# Export for different platforms
godot --headless --export-release "Windows Desktop"
godot --headless --export-release "Linux/X11"
godot --headless --export-release "macOS"
```

## Best Practices

1. **Use version control**: Track all project files in Git
2. **Test frequently**: Run the game often to catch issues early
3. **Backup before major changes**: Create a commit before big refactors
4. **Use scene inheritance**: Extend existing scenes rather than duplicating
5. **Keep scripts small**: Break complex logic into multiple scripts

## Troubleshooting

### GODOT not found
- Ensure GODOT is installed and in PATH
- Check GODOT version compatibility

### MCP connection failed
- Verify MCP server is running
- Check port configuration
- Ensure firewall allows connections

### Export failed
- Check export presets configuration
- Verify target platform is installed
- Ensure all required resources are included

## References

- [GODOT Documentation](https://docs.godotengine.org/)
- [GODOT MCP Protocol](https://github.com/godotengine/mcp)
- [GDScript Style Guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)
