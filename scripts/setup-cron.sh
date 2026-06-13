#!/bin/bash
# Setup helper script for cron-based daily repository validation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${LOG_DIR:-/var/log}"
CRON_HOUR="${CRON_HOUR:-9}"
CRON_MINUTE="${CRON_MINUTE:-0}"
EMAIL="${REPORT_EMAIL:-sathishkr.cs@gmail.com}"

echo "🔧 Setting up cron-based daily repository validation..."
echo ""
echo "Configuration:"
echo "  Repository: $REPO_DIR"
echo "  Schedule: Daily at $CRON_HOUR:$CRON_MINUTE UTC"
echo "  Email: $EMAIL"
echo "  Log directory: $LOG_DIR"
echo ""

# Check if scripts are executable
if [ ! -x "$SCRIPT_DIR/validate_and_report.sh" ]; then
  echo "⚠️  Making validate_and_report.sh executable..."
  chmod +x "$SCRIPT_DIR/validate_and_report.sh"
fi

if [ ! -x "$SCRIPT_DIR/send_daily_report.py" ]; then
  echo "⚠️  Making send_daily_report.py executable..."
  chmod +x "$SCRIPT_DIR/send_daily_report.py"
fi

# Create a wrapper script
WRAPPER_SCRIPT="/tmp/daily-repo-validation-wrapper.sh"
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
REPO_DIR="$1"
LOG_DIR="$2"
EMAIL="$3"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/repo-validation-$(date +%Y-%m-%d).log"

{
  echo "=== Repository Validation at $(date) ==="
  cd "$REPO_DIR"
  REPORT_EMAIL="$EMAIL" python3 scripts/send_daily_report.py
} >> "$LOG_FILE" 2>&1
EOF

chmod +x "$WRAPPER_SCRIPT"

# Show crontab entry
CRON_ENTRY="$CRON_MINUTE $CRON_HOUR * * * $WRAPPER_SCRIPT $REPO_DIR $LOG_DIR $EMAIL"

echo "To add this to your crontab, run:"
echo ""
echo "  crontab -e"
echo ""
echo "And add this line:"
echo "  $CRON_ENTRY"
echo ""
echo "Or run this command to add it automatically:"
echo "  (crontab -l 2>/dev/null; echo '$CRON_ENTRY') | crontab -"
echo ""
echo "To verify the cron job is installed:"
echo "  crontab -l | grep daily-repo-validation-wrapper"
echo ""
