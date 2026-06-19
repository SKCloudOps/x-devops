#!/bin/bash

# Setup Status Check Script
# Shows current configuration state and what's needed

echo ""
echo "📊 DAILY REPORTS SETUP STATUS CHECK"
echo "===================================="
echo ""

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check status
check_status() {
    echo -e "${BLUE}Repository:${NC} $(basename $REPO_DIR)"
    echo -e "${BLUE}Location:${NC} $REPO_DIR"
    echo -e "${BLUE}User Email:${NC} sathishkr.cs@gmail.com"
    echo ""
}

# Function to check Python
check_python() {
    echo -e "${BLUE}📦 Python Environment${NC}"

    if ! command -v python3 &> /dev/null; then
        echo -e "  ${RED}✗${NC} Python3 not found"
        return 1
    fi
    echo -e "  ${GREEN}✓${NC} Python3: $(python3 --version)"

    if python3 -c "import dotenv" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} python-dotenv installed"
    else
        echo -e "  ${YELLOW}⚠${NC} python-dotenv not installed"
        echo "    Run: pip install -r requirements.txt"
    fi
    echo ""
}

# Function to check .env
check_env() {
    echo -e "${BLUE}🔐 Gmail Configuration (.env)${NC}"

    if [ ! -f "$REPO_DIR/.env" ]; then
        echo -e "  ${RED}✗${NC} .env file not found"
        echo "    Run: cp .env.example .env"
        return 1
    fi

    echo -e "  ${GREEN}✓${NC} .env file exists"

    # Source .env (safely)
    source "$REPO_DIR/.env" 2>/dev/null || true

    # Check GMAIL_SENDER_EMAIL
    if [ -z "$GMAIL_SENDER_EMAIL" ]; then
        echo -e "  ${RED}✗${NC} GMAIL_SENDER_EMAIL not set"
    else
        echo -e "  ${GREEN}✓${NC} GMAIL_SENDER_EMAIL: $GMAIL_SENDER_EMAIL"
    fi

    # Check GMAIL_APP_PASSWORD
    if [ -z "$GMAIL_APP_PASSWORD" ]; then
        echo -e "  ${RED}✗${NC} GMAIL_APP_PASSWORD not set (REQUIRED)"
        echo "    Get app password from: https://myaccount.google.com/apppasswords"
        echo "    Then edit .env and add it"
    else
        PASSWORD_LENGTH=${#GMAIL_APP_PASSWORD}
        if [ $PASSWORD_LENGTH -lt 10 ]; then
            echo -e "  ${YELLOW}⚠${NC} GMAIL_APP_PASSWORD seems too short (${PASSWORD_LENGTH} chars)"
        else
            echo -e "  ${GREEN}✓${NC} GMAIL_APP_PASSWORD configured (${PASSWORD_LENGTH} chars)"
        fi
    fi

    # Check GMAIL_RECIPIENT_EMAIL
    if [ -z "$GMAIL_RECIPIENT_EMAIL" ]; then
        echo -e "  ${YELLOW}⚠${NC} GMAIL_RECIPIENT_EMAIL not set (will use default)"
    else
        echo -e "  ${GREEN}✓${NC} GMAIL_RECIPIENT_EMAIL: $GMAIL_RECIPIENT_EMAIL"
    fi

    echo ""
}

# Function to check scripts
check_scripts() {
    echo -e "${BLUE}📝 Scripts${NC}"

    SCRIPTS=(
        "send_gmail_report.py"
        "validate_and_report.py"
        "setup_daily_reports.sh"
        "check_setup_status.sh"
    )

    for script in "${SCRIPTS[@]}"; do
        if [ -f "$REPO_DIR/$script" ]; then
            echo -e "  ${GREEN}✓${NC} $script"
        else
            echo -e "  ${RED}✗${NC} $script (missing)"
        fi
    done
    echo ""
}

# Function to check cron
check_cron() {
    echo -e "${BLUE}⏰ Automation${NC}"

    if crontab -l 2>/dev/null | grep -q "send_gmail_report"; then
        echo -e "  ${GREEN}✓${NC} Cron job configured"
        echo "    $(crontab -l | grep send_gmail_report)"
    else
        echo -e "  ${YELLOW}⚠${NC} No cron job configured"
        echo "    Run: crontab -e (and add the schedule)"
        echo "    Or: bash setup_daily_reports.sh"
    fi
    echo ""
}

# Function to show recommendations
show_recommendations() {
    echo -e "${BLUE}📋 Setup Checklist${NC}"

    source "$REPO_DIR/.env" 2>/dev/null || true

    echo ""
    if [ -z "$GMAIL_APP_PASSWORD" ]; then
        echo -e "  ${YELLOW}1. REQUIRED: Add Gmail app password to .env${NC}"
        echo "     • Go to: https://myaccount.google.com/apppasswords"
        echo "     • Enable 2-factor auth if needed"
        echo "     • Generate and copy the 16-char password"
        echo "     • Edit .env and paste the password"
        echo ""
    else
        echo -e "  ${GREEN}1. ✓ Gmail credentials configured${NC}"
        echo ""
    fi

    echo -e "  2. Test the setup:"
    echo "     python3 send_gmail_report.py"
    echo ""

    if ! crontab -l 2>/dev/null | grep -q "send_gmail_report"; then
        echo -e "  3. Set up automation (choose one):"
        echo "     • Cron: crontab -e"
        echo "     • Script: bash setup_daily_reports.sh"
        echo "     • GitHub: See AUTOMATED_REPORTS_SETUP.md"
        echo ""
    else
        echo -e "  ${GREEN}3. ✓ Automation configured${NC}"
        echo ""
    fi
}

# Function to show next steps
show_next_steps() {
    echo -e "${BLUE}🚀 Next Steps${NC}"
    echo ""
    echo "1. Edit .env with your Gmail app password"
    echo "2. Test: python3 send_gmail_report.py"
    echo "3. Set up automation (cron or script)"
    echo ""
    echo "📚 For more details, see: SETUP_INSTRUCTIONS.md"
    echo ""
}

# Function to show disk space
check_disk() {
    echo -e "${BLUE}💾 Storage${NC}"

    LOGS_SIZE=0
    REPORTS_SIZE=0

    if [ -f "$REPO_DIR/report_logs.txt" ]; then
        LOGS_SIZE=$(stat -f%z "$REPO_DIR/report_logs.txt" 2>/dev/null || stat -c%s "$REPO_DIR/report_logs.txt" 2>/dev/null)
    fi

    if [ -f "$REPO_DIR/repo_validation_*.html" ]; then
        REPORTS_SIZE=$(du -sh "$REPO_DIR"/ 2>/dev/null | awk '{print $1}')
    fi

    echo -e "  ${GREEN}✓${NC} Logs: $([ -f "$REPO_DIR/report_logs.txt" ] && wc -l < "$REPO_DIR/report_logs.txt" || echo "0") lines"
    echo ""
}

# Main execution
echo ""
check_status
check_python
check_env
check_scripts
check_cron
check_disk
show_recommendations
show_next_steps
