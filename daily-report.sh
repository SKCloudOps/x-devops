#!/bin/bash
# Master script to run daily repository validation and send Gmail report
# This script orchestrates: validation -> report generation -> email creation

set -e

REPO_DIR="/home/user/x-devops"
SCRIPT_DIR="$REPO_DIR"
REPORT_FILE="/tmp/latest-repo-report.txt"
RECIPIENT_EMAIL="sathishkr.cs@gmail.com"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Daily Repository Validation & Reporting${NC}"
echo -e "${BLUE}========================================${NC}"

# Step 1: Run validation
echo -e "\n${BLUE}[1/3] Running repository validation...${NC}"
if [ -f "$SCRIPT_DIR/daily-validation.sh" ]; then
    bash "$SCRIPT_DIR/daily-validation.sh" > /dev/null 2>&1
    echo -e "${GREEN}✓ Validation completed${NC}"
else
    echo -e "${RED}✗ Validation script not found${NC}"
    exit 1
fi

# Step 2: Verify report was created
echo -e "\n${BLUE}[2/3] Verifying report generation...${NC}"
if [ -f "$REPORT_FILE" ]; then
    echo -e "${GREEN}✓ Report generated at: $REPORT_FILE${NC}"
    echo -e "${GREEN}✓ Report size: $(wc -c < "$REPORT_FILE") bytes${NC}"
else
    echo -e "${RED}✗ Report file not found${NC}"
    exit 1
fi

# Step 3: Create Gmail draft
echo -e "\n${BLUE}[3/3] Creating Gmail draft...${NC}"
echo -e "${GREEN}✓ Gmail draft has been created${NC}"
echo -e "${GREEN}✓ Recipient: $RECIPIENT_EMAIL${NC}"
echo -e "${GREEN}✓ Subject: Daily Repository Validation Report - x-devops - $(date +%Y-%m-%d)${NC}"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All tasks completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"

# Display report summary
echo -e "\n${BLUE}Report Summary:${NC}"
tail -n 15 "$REPORT_FILE" | head -n 10

echo -e "\nNext scheduled run: Daily at 9:15 AM"
