# Python Toolkit Startup Skill

## Overview

This skill provides deterministic startup and lifecycle management for Python projects.

## Prerequisites

- Python 3.8+ installed
- Package manager (pip, poetry, uv, or pipenv)

## Project Detection

### Automatic Detection
The skill automatically detects Python projects by looking for:
- `pyproject.toml` with Python project configuration
- `requirements.txt` with Python dependencies
- `uv.lock`, `poetry.lock`, or `Pipfile.lock` for package managers
- Python files (`.py`) in the project

### Explicit Configuration
Create `opencode.project.json` in the project root:

```json
{
  "version": 1,
  "projectType": "python",
  "root": ".",
  "packageManager": "poetry",
  "services": [
    {
      "id": "api",
      "cwd": ".",
      "command": ["poetry", "run", "python", "-m", "uvicorn", "main:app", "--reload"],
      "readiness": {
        "type": "http",
        "url": "http://127.0.0.1:8000",
        "timeoutSeconds": 30
      }
    }
  ],
  "checks": {
    "build": ["poetry", "build"],
    "test": ["poetry", "run", "pytest"],
    "lint": ["poetry", "run", "flake8"]
  }
}
```

## Package Manager Detection

The skill detects package managers in this order:
1. `uv.lock` → uv
2. `poetry.lock` → poetry
3. `Pipfile.lock` → pipenv
4. `requirements.txt` → pip
5. `pyproject.toml` → pip or poetry (based on build system)

## Framework Detection

The skill detects frameworks from explicit evidence only:
- **FastAPI**: `fastapi` in dependencies, `app = FastAPI()` in code
- **Flask**: `flask` in dependencies, `app = Flask(__name__)` in code
- **Django**: `django` in dependencies, `manage.py` exists
- **Custom**: No framework detected, use declared scripts

## Command Selection

The skill selects commands in this order:
1. Explicit profile command
2. Declared project scripts (e.g., `poetry run start`)
3. Framework-specific commands (only with explicit evidence)
4. Refuse if no usable command exists

## Commands

### Plan
Preview what will be done without executing:

```bash
# Preview startup plan
poetry run python -m uvicorn main:app --reload --dry-run
```

### Run
Start the Python application:

```bash
# Using poetry
poetry run python -m uvicorn main:app --reload

# Using uv
uv run python -m uvicorn main:app --reload

# Using pipenv
pipenv run python -m uvicorn main:app --reload

# Using pip (with venv)
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn main:app --reload
```

### Status
Check if the application is running:

```bash
# Check if Python process is running
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I "python.exe" > NUL
if %ERRORLEVEL% == 0 (
    echo Python process is running
) else (
    echo Python process is not running
)

# Check HTTP endpoint
curl -s http://127.0.0.1:8000 > /dev/null
if %ERRORLEVEL% == 0 (
    echo Server is responding
) else (
    echo Server is not responding
)
```

### Stop
Stop the application:

```bash
# Stop Python process
taskkill /IM python.exe /F

# Or use package manager script
poetry run stop
```

## Best Practices

1. **Use explicit configuration**: Always create `opencode.project.json` for production
2. **Prefer declared scripts**: Use project scripts over framework-specific commands
3. **Don't guess frameworks**: Only detect frameworks with explicit evidence
4. **Require selection**: When multiple entrypoints exist, require user selection
5. **Test frequently**: Run the application often to catch issues early

## Troubleshooting

### Port already in use
- Check if another process is using the port
- Kill the conflicting process
- Configure a different port in `opencode.project.json`

### Command not found
- Ensure package manager is installed
- Check if dependencies are installed
- Verify virtual environment is activated

### Application not responding
- Check if the application started successfully
- Verify the correct port is configured
- Check for errors in the console
- Ensure database or other services are running

### Multiple entrypoints detected
- Specify the entrypoint in `opencode.project.json`
- Use explicit command configuration
- Do not guess between frameworks
