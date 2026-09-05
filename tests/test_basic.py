"""Basic tests for OpenCode Automation scripts."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".opencode" / "scripts"))


def test_template_validator():
    """Test template validation."""
    try:
        from template_validator import validate_template, validate_all_templates
    except ImportError:
        print("Skipping test_template_validator: template_validator module not found")
        return
    
    # Create a test template
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""## Metadata
- **Type**: feature
- **Scope**: repository

## Description
Test description

## Acceptance Criteria
- [ ] Test criterion
""")
        test_file = Path(f.name)
    
    try:
        valid, errors = validate_template(test_file)
        assert valid, f"Template validation failed: {errors}"
    finally:
        test_file.unlink()


def test_project_profile_validator():
    """Test project profile validation."""
    from project_profile import validate_profile
    
    # Valid profile
    valid_profile = {
        "version": 1,
        "projectType": "react",
        "root": "."
    }
    
    errors = validate_profile(valid_profile)
    assert len(errors) == 0, f"Valid profile has errors: {errors}"
    
    # Invalid profile
    invalid_profile = {
        "version": 999,
        "projectType": "invalid"
    }
    
    errors = validate_profile(invalid_profile)
    assert len(errors) > 0, "Invalid profile should have errors"


def test_context_resolver():
    """Test context resolution."""
    from context import resolve_target
    
    # Test with explicit repo
    class Args:
        repo = str(Path.cwd())
        source_root = None
        state_root = None
        support_root = None
    
    result = resolve_target(Args())
    assert "canonicalPath" in result, "Result should have canonicalPath"
    assert "managed" in result, "Result should have managed"


def test_worktree_script():
    """Test worktree script imports."""
    import worktree
    assert hasattr(worktree, 'create'), "worktree should have create function"
    assert hasattr(worktree, 'listing'), "worktree should have listing function"
    assert hasattr(worktree, 'remove'), "worktree should have remove function"


def test_repository_script():
    """Test repository script imports."""
    import repository
    assert hasattr(repository, 'add_repository'), "repository should have add_repository function"
    assert hasattr(repository, 'list_repositories'), "repository should have list_repositories function"


def test_process_manager():
    """Test process manager imports."""
    import process_manager
    assert hasattr(process_manager, 'start_process'), "process_manager should have start_process function"
    assert hasattr(process_manager, 'stop_process'), "process_manager should have stop_process function"


def test_command_runner():
    """Test command runner imports."""
    import command_runner
    assert hasattr(command_runner, 'run_command'), "command_runner should have run_command function"
    assert hasattr(command_runner, 'wait_for_condition'), "command_runner should have wait_for_condition function"


def test_opencode_json_valid():
    """Test opencode.json is valid JSON."""
    opencode_json = Path(__file__).parent.parent / "opencode.json"
    if opencode_json.exists():
        with open(opencode_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "instructions" in data, "opencode.json should have instructions"


def test_skills_exist():
    """Test that expected skills exist."""
    skills_dir = Path(__file__).parent.parent / ".opencode" / "skills"
    expected_skills = [
        "worktree",
        "github-issues",
        "github-management",
        "analyze",
        "code-review",
        "cluster-ssh",
        "cluster-scp",
        "package-management",
        "repository",
        "toolkit-startup-react",
        "toolkit-startup-node",
        "toolkit-startup-python",
        "toolkit-startup-dotnet",
        "toolkit-startup-godot"
    ]
    
    for skill in expected_skills:
        skill_dir = skills_dir / skill
        skill_file = skill_dir / "SKILL.md"
        assert skill_file.exists(), f"Skill {skill} should exist"


def test_commands_exist():
    """Test that expected commands exist."""
    commands_dir = Path(__file__).parent.parent / ".opencode" / "commands"
    expected_commands = [
        "worktree/create.md",
        "worktree/list.md",
        "worktree/remove.md",
        "worktree/cleanup.md",
        "issue/analyze.md",
        "issue/create.md",
        "issue/fix.md",
        "issue/migrate.md",
        "review/cr.md",
        "review/fix-cr.md",
        "sync/pull.md",
        "sync/push.md",
        "sync/ship.md"
    ]
    
    for command in expected_commands:
        command_file = commands_dir / command
        assert command_file.exists(), f"Command {command} should exist"


def test_instructions_exist():
    """Test that expected instructions exist."""
    instructions_dir = Path(__file__).parent.parent / ".opencode" / "instructions"
    expected_instructions = [
        "general.md",
        "coding-standards.md",
        "github.md",
        "worktrees.md"
    ]
    
    for instruction in expected_instructions:
        instruction_file = instructions_dir / instruction
        assert instruction_file.exists(), f"Instruction {instruction} should exist"


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_template_validator,
        test_project_profile_validator,
        test_context_resolver,
        test_worktree_script,
        test_repository_script,
        test_process_manager,
        test_command_runner,
        test_opencode_json_valid,
        test_skills_exist,
        test_commands_exist,
        test_instructions_exist
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
