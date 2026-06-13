#!/bin/bash

# Repository Validation and Daily Report Generator
# Generates a report of new commits and changes from the base branch

set -euo pipefail

REPO_PATH="${REPO_PATH:-.}"
BASE_BRANCH="${BASE_BRANCH:-main}"
CURRENT_BRANCH=$(git -C "$REPO_PATH" rev-parse --abbrev-ref HEAD)
REPORT_FILE="/tmp/repo_validation_report.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')

# Initialize report
cat > "$REPORT_FILE" << EOF
===============================================
Repository Validation Report
===============================================
Date: $TIMESTAMP
Repository: $(basename "$REPO_PATH")
Current Branch: $CURRENT_BRANCH
Base Branch: $BASE_BRANCH

EOF

# Function to validate repository
validate_repo() {
  echo "=== Repository Status ===" >> "$REPORT_FILE"

  # Check if repository is clean
  if git -C "$REPO_PATH" diff-index --quiet HEAD --; then
    echo "✓ Working directory is clean" >> "$REPORT_FILE"
  else
    echo "⚠ Working directory has uncommitted changes:" >> "$REPORT_FILE"
    git -C "$REPO_PATH" status --short >> "$REPORT_FILE"
  fi

  echo "" >> "$REPORT_FILE"
}

# Function to get new commits
get_new_commits() {
  echo "=== New Commits (last 24 hours) ===" >> "$REPORT_FILE"

  COMMITS=$(git -C "$REPO_PATH" log --since="24 hours ago" --oneline 2>/dev/null | wc -l)

  if [ "$COMMITS" -gt 0 ]; then
    echo "Found $COMMITS new commit(s):" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    git -C "$REPO_PATH" log --since="24 hours ago" --pretty=format:"%h | %an | %s | %ar" >> "$REPORT_FILE"
  else
    echo "No new commits in the last 24 hours" >> "$REPORT_FILE"
  fi

  echo "" >> "$REPORT_FILE"
}

# Function to compare with base branch
compare_with_base() {
  echo "=== Comparison with Base Branch ($BASE_BRANCH) ===" >> "$REPORT_FILE"

  # Fetch latest from origin to ensure we have latest base branch
  git -C "$REPO_PATH" fetch origin "$BASE_BRANCH" 2>/dev/null || true

  COMMITS_AHEAD=$(git -C "$REPO_PATH" rev-list --count "origin/$BASE_BRANCH..$CURRENT_BRANCH" 2>/dev/null || echo 0)
  COMMITS_BEHIND=$(git -C "$REPO_PATH" rev-list --count "$CURRENT_BRANCH..origin/$BASE_BRANCH" 2>/dev/null || echo 0)

  echo "Commits ahead of base: $COMMITS_AHEAD" >> "$REPORT_FILE"
  echo "Commits behind base: $COMMITS_BEHIND" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"

  if [ "$COMMITS_AHEAD" -gt 0 ]; then
    echo "Commits on current branch not in base:" >> "$REPORT_FILE"
    git -C "$REPO_PATH" log "origin/$BASE_BRANCH..$CURRENT_BRANCH" --oneline 2>/dev/null | head -20 >> "$REPORT_FILE"
  fi

  echo "" >> "$REPORT_FILE"
}

# Function to get file changes statistics
get_file_changes() {
  echo "=== File Changes (last 24 hours) ===" >> "$REPORT_FILE"

  FILES=$(git -C "$REPO_PATH" diff --name-only --since="24 hours ago" 2>/dev/null | sort | uniq | wc -l)

  if [ "$FILES" -gt 0 ]; then
    echo "Files modified: $FILES" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "Modified files:" >> "$REPORT_FILE"
    git -C "$REPO_PATH" diff --name-only --since="24 hours ago" 2>/dev/null | sort | uniq >> "$REPORT_FILE"
  else
    echo "No file changes in the last 24 hours" >> "$REPORT_FILE"
  fi

  echo "" >> "$REPORT_FILE"
}

# Function to check git health
check_git_health() {
  echo "=== Repository Health ===" >> "$REPORT_FILE"

  # Check for dangling objects
  DANGLING=$(git -C "$REPO_PATH" fsck --lost-found 2>/dev/null | grep -c "dangling" || echo 0)

  if [ "$DANGLING" -eq 0 ]; then
    echo "✓ No dangling objects found" >> "$REPORT_FILE"
  else
    echo "⚠ Found $DANGLING dangling object(s)" >> "$REPORT_FILE"
  fi

  echo "" >> "$REPORT_FILE"
}

# Generate report summary
generate_summary() {
  echo "=== Summary ===" >> "$REPORT_FILE"
  echo "Report generated: $TIMESTAMP" >> "$REPORT_FILE"
  echo "Repository validated successfully" >> "$REPORT_FILE"
}

# Main execution
main() {
  if [ ! -d "$REPO_PATH/.git" ]; then
    echo "Error: Not a git repository at $REPO_PATH" >&2
    exit 1
  fi

  validate_repo
  get_new_commits
  compare_with_base
  get_file_changes
  check_git_health
  generate_summary

  # Output report path for use by other scripts
  echo "$REPORT_FILE"
}

main "$@"
