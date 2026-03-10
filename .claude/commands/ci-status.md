---
description: Check GitHub Actions workflow status
allowed-tools: Bash(gh run:*)
---

# CI Status

## Recent Workflow Runs

!`gh run list --limit 10`

## Current Branch Status

!`gh run list --branch $(git branch --show-current) --limit 5`

## Usage

- View specific run: `gh run view <run-id>`
- View logs: `gh run view <run-id> --log`
- Re-run failed: `gh run rerun <run-id>`
