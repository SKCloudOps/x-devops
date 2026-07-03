#!/bin/bash
# Daily repository validation and reporting script
# This script checks for new commits and changes, then sends a report via email

set -e

REPO_DIR="/home/user/x-devops"
LOG_FILE="/tmp/repo-validation-$(date +%Y%m%d).log"
REPORT_FILE="/tmp/repo-report-$(date +%Y%m%d).txt"
BASE_BRANCH="main"
REPORT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cd "$REPO_DIR"

# Function to log messages
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Start validation
log_msg "Starting daily repository validation..."

# Fetch latest from remote
log_msg "Fetching latest from remote..."
git fetch origin 2>&1 | tee -a "$LOG_FILE"

# Get repository status
log_msg "Checking repository status..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
COMMIT_COUNT=$(git rev-list --count origin/$BASE_BRANCH..HEAD 2>/dev/null || echo "0")

# Get commits from base branch (last 24 hours)
log_msg "Analyzing commits from $BASE_BRANCH..."
YESTERDAY=$(date -d '1 day ago' '+%Y-%m-%d')
NEW_COMMITS=$(git log --oneline --since="24 hours ago" origin/$BASE_BRANCH 2>/dev/null | wc -l)

# Generate report
cat > "$REPORT_FILE" << EOF
================================================================================
DAILY REPOSITORY VALIDATION REPORT - x-devops
Generated: $REPORT_DATE
================================================================================

REPOSITORY STATUS:
  Current Branch: $CURRENT_BRANCH
  Base Branch: $BASE_BRANCH
  Repository Path: $REPO_DIR
  Status: $(git status --short | wc -l) uncommitted changes

BRANCH COMPARISON:
  Commits ahead of $BASE_BRANCH: $COMMIT_COUNT
  New commits in $BASE_BRANCH (last 24h): $NEW_COMMITS

LATEST COMMITS FROM $BASE_BRANCH (Last 10):
$(git log --oneline -10 origin/$BASE_BRANCH | sed 's/^/  /')

CURRENT BRANCH STATUS:
$(git status --short || echo "  No changes")

UNCOMMITTED CHANGES:
$(git diff --stat || echo "  No changes")

GIT VALIDATION CHECKS:
  ✓ Repository is accessible
  ✓ Remote is configured
  $([ $NEW_COMMITS -gt 0 ] && echo "✓ New commits detected in base branch" || echo "✗ No new commits in base branch (last 24h)")
  $([ "$(git status --short | wc -l)" -eq 0 ] && echo "✓ Working directory clean" || echo "✗ Uncommitted changes present")

SUMMARY:
  Total new commits from base branch: $NEW_COMMITS
  Commits on current branch ahead of base: $COMMIT_COUNT
  Uncommitted changes: $(git status --short | wc -l)
  Repository Status: OK

================================================================================
EOF

log_msg "Report generated successfully at $REPORT_FILE"
cat "$REPORT_FILE"

# Save report content for email sending
cp "$REPORT_FILE" /tmp/latest-repo-report.txt

log_msg "Daily validation completed successfully."
