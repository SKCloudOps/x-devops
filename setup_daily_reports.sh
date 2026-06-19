#!/bin/bash

# Daily Repository Validation Reports - Setup Script
# This script helps you configure and test the daily email reports

set -e

echo "🔧 Setting up Daily Repository Validation Reports"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# Function to check if .env exists and is configured
check_env_file() {
    echo "1️⃣  Checking .env configuration..."

    if [ ! -f "$REPO_DIR/.env" ]; then
        echo -e "${RED}✗${NC} .env file not found"
        return 1
    fi

    source "$REPO_DIR/.env"

    if [ -z "$GMAIL_SENDER_EMAIL" ]; then
        echo -e "${RED}✗${NC} GMAIL_SENDER_EMAIL not set"
        return 1
    fi

    if [ -z "$GMAIL_APP_PASSWORD" ]; then
        echo -e "${RED}✗${NC} GMAIL_APP_PASSWORD not set (REQUIRED)"
        echo ""
        echo "To get your Gmail app password:"
        echo "1. Go to: https://myaccount.google.com/security"
        echo "2. Enable 2-Step Verification (if not already enabled)"
        echo "3. Go to: https://myaccount.google.com/apppasswords"
        echo "4. Select Mail → Windows Computer"
        echo "5. Copy the 16-character password and add to .env"
        return 1
    fi

    if [ -z "$GMAIL_RECIPIENT_EMAIL" ]; then
        echo -e "${YELLOW}⚠${NC}  GMAIL_RECIPIENT_EMAIL not set, will use default"
        return 0
    fi

    echo -e "${GREEN}✓${NC} .env file is configured"
    echo "   Sender: $GMAIL_SENDER_EMAIL"
    echo "   Recipient: $GMAIL_RECIPIENT_EMAIL"
    return 0
}

# Function to check Python dependencies
check_dependencies() {
    echo ""
    echo "2️⃣  Checking Python dependencies..."

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗${NC} Python3 not found"
        return 1
    fi

    python3 -c "import dotenv" 2>/dev/null || {
        echo -e "${YELLOW}⚠${NC}  python-dotenv not installed. Installing..."
        pip install -r "$REPO_DIR/requirements.txt"
    }

    echo -e "${GREEN}✓${NC} Dependencies are installed"
    return 0
}

# Function to test the setup
test_setup() {
    echo ""
    echo "3️⃣  Testing repository validation and email sending..."

    python3 "$REPO_DIR/send_gmail_report.py"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Setup test passed!"
        return 0
    else
        echo -e "${RED}✗${NC} Setup test failed. Check your configuration."
        return 1
    fi
}

# Function to setup cron job
setup_cron() {
    echo ""
    echo "4️⃣  Setting up cron job for daily reports..."

    CRON_ENTRY="0 9 * * * cd $REPO_DIR && python3 $REPO_DIR/send_gmail_report.py >> $REPO_DIR/report_logs.txt 2>&1"

    # Check if cron entry already exists
    if crontab -l 2>/dev/null | grep -q "send_gmail_report.py"; then
        echo -e "${YELLOW}⚠${NC}  Cron job already exists"
        echo "   To modify, run: crontab -e"
        return 0
    fi

    # Add cron entry
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

    echo -e "${GREEN}✓${NC} Cron job added - reports will be sent daily at 9 AM"
    echo "   Command: $CRON_ENTRY"
    return 0
}

# Function to display summary
display_summary() {
    echo ""
    echo "=================================================="
    echo "📋 Setup Summary"
    echo "=================================================="
    echo ""
    echo "✅ Configuration:"
    echo "   • Repository: $(basename $REPO_DIR)"
    echo "   • Reports scheduled: Daily at 9 AM"
    echo "   • Report format: HTML email with git analysis"
    echo ""
    echo "✅ Reports will include:"
    echo "   • Repository status and current branch"
    echo "   • Uncommitted changes count"
    echo "   • New commits from main branch (last 24h)"
    echo "   • Detailed commit list with authors and messages"
    echo ""
    echo "📧 To view logs:"
    echo "   tail -f $REPO_DIR/report_logs.txt"
    echo ""
    echo "🔧 To modify schedule:"
    echo "   crontab -e"
    echo ""
}

# Main execution
main() {
    echo ""

    if ! check_env_file; then
        echo ""
        echo -e "${RED}❌ Please configure .env file first:${NC}"
        echo ""
        echo "Edit: $REPO_DIR/.env"
        echo "And set GMAIL_APP_PASSWORD with your 16-character app password"
        echo ""
        return 1
    fi

    if ! check_dependencies; then
        echo -e "${RED}❌ Dependency check failed${NC}"
        return 1
    fi

    if ! test_setup; then
        echo -e "${RED}❌ Setup test failed${NC}"
        return 1
    fi

    if ! setup_cron; then
        echo -e "${YELLOW}⚠${NC}  Cron setup had issues"
        return 1
    fi

    display_summary
    echo -e "${GREEN}✅ Setup complete!${NC}"
}

main "$@"
