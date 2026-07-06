#!/bin/bash

# Daily validation and reporting script
# This script runs the repository validation and sends a report via Gmail

cd /home/user/x-devops

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "Error: .env file not found. Please create it with Gmail credentials."
    exit 1
fi

# Run the validation and send report
python3 send_gmail_report.py

# Log the result
EXIT_CODE=$?
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$TIMESTAMP] ✅ Daily validation completed successfully" >> /home/user/x-devops/validation_logs.txt
else
    echo "[$TIMESTAMP] ❌ Daily validation failed with exit code $EXIT_CODE" >> /home/user/x-devops/validation_logs.txt
fi

exit $EXIT_CODE
