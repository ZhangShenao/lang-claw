---
description: Create a pull request with auto-generated description
argument-hint: [title]
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(gh pr create:*), Bash(gh pr view:*)
---

# Create Pull Request

## Context

- Current branch: !`git branch --show-current`
- Base branch (main): !`git remote show origin | grep 'HEAD branch' | cut -d':' -f2 | tr -d ' '`
- Commits in this branch: !`git log origin/master..HEAD --oneline 2>/dev/null || git log master..HEAD --oneline`
- Changed files: !`git diff origin/master...HEAD --stat 2>/dev/null || git diff master...HEAD --stat`

## Task

### Step 1: Verify Branch Status

Ensure:
- All changes are committed
- Branch is pushed to remote
- No merge conflicts

### Step 2: Generate PR Description

Create a PR description with:

```markdown
## Summary
[Brief description of what this PR does]

## Changes
- [List key changes as bullet points]

## Test Plan
[Checklist of how to test these changes]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Step 3: Create PR

Use `gh pr create` with:
- Title based on the main commit or provided argument
- Body with the generated description
- Base branch: master (or main)

## Example Command

```bash
gh pr create --base master --title "<title>" --body "<description>"
```

## Output

Report:
1. PR URL
2. PR number
3. CI status (if available)
