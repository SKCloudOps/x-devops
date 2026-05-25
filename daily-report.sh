#!/bin/bash

# Daily Repository Validation and Report Generator
# Monitors new commits and changes from base branch

REPO_NAME="x-devops"
BASE_BRANCH="main"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
EMAIL="sathishkr.cs@gmail.com"
REPORT_FILE="/tmp/repo-report-$(date +%Y%m%d).txt"

echo "=== Daily Repository Validation Report ===" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "Repository: $REPO_NAME" >> "$REPORT_FILE"
echo "Current Branch: $CURRENT_BRANCH" >> "$REPORT_FILE"
echo "Base Branch: $BASE_BRANCH" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Fetch latest from origin
echo "Fetching latest changes..." >> "$REPORT_FILE"
git fetch origin >> "$REPORT_FILE" 2>&1

# Check for new commits in base branch since last check
echo "" >> "$REPORT_FILE"
echo "=== NEW COMMITS IN BASE BRANCH ===" >> "$REPORT_FILE"
git log origin/$BASE_BRANCH --oneline -10 >> "$REPORT_FILE"

# Get diff summary between current branch and base branch
echo "" >> "$REPORT_FILE"
echo "=== CHANGES COMPARISON ===" >> "$REPORT_FILE"
echo "Files changed:" >> "$REPORT_FILE"
git diff --name-status origin/$BASE_BRANCH..HEAD >> "$REPORT_FILE" 2>/dev/null || echo "No differences" >> "$REPORT_FILE"

# Get commit stats
echo "" >> "$REPORT_FILE"
echo "=== COMMIT STATISTICS ===" >> "$REPORT_FILE"
echo "Commits ahead of $BASE_BRANCH:" >> "$REPORT_FILE"
git rev-list --count origin/$BASE_BRANCH..HEAD >> "$REPORT_FILE"

# Repository validation checks
echo "" >> "$REPORT_FILE"
echo "=== REPOSITORY STATUS ===" >> "$REPORT_FILE"
echo "Git status:" >> "$REPORT_FILE"
git status --short >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "=== BRANCH INFO ===" >> "$REPORT_FILE"
git branch -vv >> "$REPORT_FILE"

# Display the report
echo "Report generated successfully!"
cat "$REPORT_FILE"

# Save report path for email sending
echo "$REPORT_FILE"
