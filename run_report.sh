#!/bin/bash

# Simple wrapper to run the daily report
# Usage: ./run_report.sh or bash run_report.sh

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "📊 Running Repository Validation Report..."
echo ""

python3 daily_repo_report.py

echo ""
echo "✅ Report complete!"
echo "📁 Local reports saved to: $REPO_DIR/reports/"
echo "📧 Check your email for the sent report"
