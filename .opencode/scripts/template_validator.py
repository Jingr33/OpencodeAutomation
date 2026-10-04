"""Template validation for OpenCode Automation."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def validate_issue_task(content: str) -> list[str]:
    """Validate issue-task.md template."""
    errors = []
    
    # Check required sections
    if "## Metadata" not in content:
        errors.append("Missing required section: ## Metadata")
    
    if "## Description" not in content:
        errors.append("Missing required section: ## Description")
    
    if "## Acceptance Criteria" not in content:
        errors.append("Missing required section: ## Acceptance Criteria")
    
    # Check metadata fields
    if "- **Type**:" not in content:
        errors.append("Missing metadata field: Type")
    
    if "- **Scope**:" not in content:
        errors.append("Missing metadata field: Scope")
    
    return errors


def validate_issue_analysis(content: str) -> list[str]:
    """Validate issue-analysis.md template."""
    errors = []
    
    # Check required sections
    if "## Summary" not in content:
        errors.append("Missing required section: ## Summary")
    
    if "## Analysis" not in content:
        errors.append("Missing required section: ## Analysis")
    
    if "## Recommendations" not in content:
        errors.append("Missing required section: ## Recommendations")
    
    return errors


def validate_summary(content: str) -> list[str]:
    """Validate summary.md template."""
    errors = []
    
    # Check required sections
    if "## Task" not in content:
        errors.append("Missing required section: ## Task")
    
    if "## Changes" not in content:
        errors.append("Missing required section: ## Changes")
    
    if "## Verification" not in content:
        errors.append("Missing required section: ## Verification")
    
    return errors


def validate_fix(content: str) -> list[str]:
    """Validate fix.md template."""
    errors = []
    
    # Check required sections
    if "## Issue" not in content:
        errors.append("Missing required section: ## Issue")
    
    if "## Root Cause" not in content:
        errors.append("Missing required section: ## Root Cause")
    
    if "## Solution" not in content:
        errors.append("Missing required section: ## Solution")
    
    return errors


def validate_fix_cr(content: str) -> list[str]:
    """Validate fix-cr.md template."""
    errors = []
    
    # Check required sections
    if "## Review" not in content:
        errors.append("Missing required section: ## Review")
    
    if "## Changes" not in content:
        errors.append("Missing required section: ## Changes")
    
    return errors


def validate_pr_title(content: str) -> list[str]:
    """Validate pr-title.md template."""
    errors = []
    
    # Check required format
    if not re.match(r'^(feat|fix|docs|style|refactor|test|chore):', content):
        errors.append("PR title must start with type prefix (feat|fix|docs|style|refactor|test|chore)")
    
    return errors


def validate_template(path: Path) -> tuple[bool, list[str]]:
    """Validate a template file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return False, [f"Template file not found: {path}"]
    
    # Select validator based on filename
    filename = path.name
    if filename == "issue-task.md":
        errors = validate_issue_task(content)
    elif filename == "issue-analysis.md":
        errors = validate_issue_analysis(content)
    elif filename == "summary.md":
        errors = validate_summary(content)
    elif filename == "fix.md":
        errors = validate_fix(content)
    elif filename == "fix-cr.md":
        errors = validate_fix_cr(content)
    elif filename == "pr-title.md":
        errors = validate_pr_title(content)
    else:
        errors = [f"Unknown template type: {filename}"]
    
    return len(errors) == 0, errors


def validate_all_templates(templates_dir: Path) -> dict[str, Any]:
    """Validate all templates in directory."""
    results = {}
    
    for template_file in templates_dir.glob("*.md"):
        valid, errors = validate_template(template_file)
        results[template_file.name] = {
            "valid": valid,
            "errors": errors
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Template validation")
    parser.add_argument("--templates-dir", help="Templates directory path")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    templates_dir = Path(args.templates_dir) if args.templates_dir else Path(__file__).parent.parent / "templates"
    
    if not templates_dir.exists():
        print(f"Templates directory not found: {templates_dir}")
        return 1
    
    results = validate_all_templates(templates_dir)
    
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        all_valid = True
        for template_name, result in results.items():
            if result["valid"]:
                print(f"✓ {template_name}")
            else:
                print(f"✗ {template_name}")
                for error in result["errors"]:
                    print(f"  - {error}")
                all_valid = False
        
        if all_valid:
            print("\nAll templates are valid")
        else:
            print("\nSome templates have errors")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
