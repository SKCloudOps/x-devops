#!/bin/bash

# Daily Repository Validation Task
# Runs validation and sends report via Gmail

set -e

REPO_DIR="/home/user/x-devops"
SCRIPTS_DIR="$REPO_DIR/scripts"
LOG_FILE="$REPO_DIR/.validation-logs/$(date '+%Y-%m-%d').log"
RECIPIENT="${GMAIL_RECIPIENT:-sathishkr.cs@gmail.com}"

# Create log directory if it doesn't exist
mkdir -p "$REPO_DIR/.validation-logs"

# Change to repo directory
cd "$REPO_DIR"

# Run the validation
echo "Starting daily repository validation at $(date '+%Y-%m-%d %H:%M:%S UTC')" | tee -a "$LOG_FILE"

# Execute validation and capture output
VALIDATION_OUTPUT=$("$SCRIPTS_DIR/daily-repo-validation.sh" 2>&1)

# Send the report
echo "$VALIDATION_OUTPUT" | "$SCRIPTS_DIR/send-validation-report.sh" "$RECIPIENT" | tee -a "$LOG_FILE"

echo "Daily validation completed at $(date '+%Y-%m-%d %H:%M:%S UTC')" >> "$LOG_FILE"

# Clean up old logs (keep last 30 days)
find "$REPO_DIR/.validation-logs" -name "*.log" -mtime +30 -delete

exit 0
