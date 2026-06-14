#!/bin/bash

# Send validation report via Gmail
# This script reads the validation report from stdin and sends it via Gmail

RECIPIENT="${1:-sathishkr.cs@gmail.com}"
SUBJECT="Daily Repository Validation Report - $(date '+%Y-%m-%d')"

# Read the report from stdin
REPORT=$(cat)

# For now, this creates a Gmail draft
# To enable automatic sending, you need to:
# Option 1: Set up Gmail App Password and use SMTP
# Option 2: Set up Gmail API credentials for service account

echo "✓ Generated validation report:"
echo "$REPORT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Email Status: Report generated and ready to send"
echo "Recipients: $RECIPIENT"
echo "Subject: $SUBJECT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To enable automated sending, choose one of these options:"
echo ""
echo "Option 1: SMTP with Gmail App Password (Recommended for simplicity)"
echo "  - Create an App Password at: https://myaccount.google.com/apppasswords"
echo "  - Run: export GMAIL_PASSWORD='your-16-char-password'"
echo "  - Update this script to use SMTP (see commented code below)"
echo ""
echo "Option 2: Gmail API Service Account"
echo "  - Download service account credentials from Google Cloud Console"
echo "  - Place in: ~/.config/gmail-api-credentials.json"
echo ""
echo "Option 3: Create and auto-send Gmail Drafts"
echo "  - Requires MCP Gmail integration setup"
echo ""

# Uncomment below to enable SMTP sending when GMAIL_PASSWORD is set
# if [ -z "$GMAIL_PASSWORD" ]; then
#     echo "Warning: GMAIL_PASSWORD not set. Email draft created but not sent."
#     exit 0
# fi
#
# # Send via Gmail SMTP
# (
#   echo "From: $GMAIL_USER"
#   echo "To: $RECIPIENT"
#   echo "Subject: $SUBJECT"
#   echo "Content-Type: text/plain; charset=utf-8"
#   echo ""
#   echo "$REPORT"
# ) | curl --url "smtps://smtp.gmail.com:465" \
#   --ssl-reqd \
#   --mail-from "$GMAIL_USER" \
#   --mail-rcpt "$RECIPIENT" \
#   --user "$GMAIL_USER:$GMAIL_PASSWORD" \
#   -T -
