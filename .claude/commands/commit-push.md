---
description: Generate commit message and push changes to remote branch
argument-hint: [message]
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*)
---

# Commit & Push

## Context

- Current branch: !`git branch --show-current`
- Git status: !`git status`
- Recent commits: !`git log --oneline -5`

## Changes to Commit

!`git diff --staged`

## Task

### Step 1: Generate Commit Message

Analyze the staged changes and generate a commit message following these conventions:

1. **Format**: `<type>(<scope>): <description>`
2. **Types**: feat, fix, docs, style, refactor, test, chore
3. **Keep it concise** (under 72 characters for the title)
4. **Reference issues** if applicable

### Step 2: Commit

Execute:
```bash
git commit -m "<generated message>"
```

### Step 3: Push

Push to remote with:
```bash
git push origin $(git branch --show-current)
```

## Important Rules

- NEVER use `git add .` - only commit already staged files
- NEVER use `--no-verify` or skip hooks
- NEVER amend existing commits unless explicitly requested
- Always verify the commit was successful before pushing

## Output

After completion, report:
1. The commit message used
2. The commit hash
3. Push status
