---
description: Perform automated code review on staged or recent changes
argument-hint: [all|staged|last-commit]
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git status:*), Bash(git log:*)
---

# Code Review

## Context

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`

## Task

Perform a comprehensive code review on the specified scope:

### Scope: $ARGUMENTS (default: staged)

Based on the scope parameter:
- `all` - Review all uncommitted changes
- `staged` - Review only staged changes (default)
- `last-commit` - Review changes in the last commit

## Review Checklist

### Security (Critical)
- [ ] No hardcoded secrets/credentials
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Proper input validation
- [ ] Secure authentication/authorization

### Code Quality
- [ ] Code is readable and well-organized
- [ ] Functions/methods are appropriately sized
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Type safety where applicable

### Best Practices
- [ ] Follows project conventions (see CLAUDE.md)
- [ ] No unnecessary complexity
- [ ] Proper documentation for complex logic
- [ ] Tests are included for new functionality

### Performance
- [ ] No obvious performance issues
- [ ] Efficient database queries
- [ ] No memory leaks

## Output Format

```markdown
## Code Review Report

### Critical Issues (Must Fix)
[List any blocking issues]

### Warnings (Should Fix)
[List important but non-blocking issues]

### Suggestions (Nice to Have)
[List improvement opportunities]

### Summary
- **Risk Level**: HIGH/MEDIUM/LOW
- **Ready for Commit**: YES/NO
- **Recommended Actions**: [List]
```

If no critical issues are found, conclude with: "Code review passed. Ready to commit."
