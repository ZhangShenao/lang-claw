---
description: Show DevOps workflow guide and current status
allowed-tools: Bash(git status:*), Bash(git branch:*), Bash(gh run:*), Bash(gh pr:*)
---

# DevOps Workflow Guide

## Current Status

- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Remote: !`git remote -v | head -1`

## Available Slash Commands

### `/review [scope]`
Perform automated code review before committing.
- `staged` - Review staged changes (default)
- `all` - Review all uncommitted changes
- `last-commit` - Review the last commit

### `/commit-push [message]`
Generate commit message and push to remote.

### `/pr [title]`
Create a pull request with auto-generated description.

## Complete Workflow

```
1. Make code changes
2. Stage changes: git add <files>
3. Run: /review staged
4. Fix any critical issues
5. Run: /commit-push
6. Run: /pr
7. GitHub Actions runs tests automatically
```

## GitHub Actions

After pushing, the test pipeline automatically:
- Sets up Python 3.12
- Installs dependencies with uv
- Runs linting (ruff)
- Runs type checking (mypy)
- Runs unit tests (pytest)

Check workflow status: `gh run list --limit 5`

## Hooks

Pre-configured hooks:
- **Pre-commit**: Validates commit safety
- **Pre-push**: Checks tests and branch status
- **Post-push**: Reports GitHub Actions status
