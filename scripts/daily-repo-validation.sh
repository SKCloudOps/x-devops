#!/bin/bash

# Daily repository validation script
# Checks for new commits and changes from the base branch

BASE_BRANCH="${1:-main}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")

# Fetch latest from origin
git fetch origin "$BASE_BRANCH" 2>/dev/null || true

# Get commits on base branch since last run (24 hours)
BASE_COMMITS=$(git log origin/"$BASE_BRANCH" --since="24 hours ago" --oneline 2>/dev/null | wc -l)

# Get commits in current branch not in base branch
AHEAD_COMMITS=$(git rev-list --count origin/"$BASE_BRANCH"..origin/"$CURRENT_BRANCH" 2>/dev/null || echo "0")

# Get file changes between branches
CHANGED_FILES=$(git diff origin/"$BASE_BRANCH"...origin/"$CURRENT_BRANCH" --name-only 2>/dev/null | wc -l)

# Get untracked files
UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)

# Build report
REPORT_TIME=$(date '+%Y-%m-%d %H:%M:%S UTC')
REPORT="Repository Validation Report
========================================
Repository: $REPO_NAME
Generated: $REPORT_TIME

SUMMARY:
--------
Base Branch ($BASE_BRANCH): $BASE_COMMITS new commits in last 24 hours
Current Branch ($CURRENT_BRANCH): $AHEAD_COMMITS commits ahead of base
Changed Files: $CHANGED_FILES
Untracked Files: $UNTRACKED

LAST 5 COMMITS ON BASE BRANCH:
$(git log origin/"$BASE_BRANCH" -5 --oneline 2>/dev/null)

LAST 5 COMMITS ON CURRENT BRANCH:
$(git log origin/"$CURRENT_BRANCH" -5 --oneline 2>/dev/null)

STATUS: Working tree is $([ -z "$(git status --porcelain)" ] && echo "clean" || echo "DIRTY")"

echo "$REPORT"
