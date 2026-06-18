#!/bin/bash

# Daily Repository Validation Reports Setup Script
# This script helps configure automated daily repository validation reports

echo "🚀 Repository Validation Report Setup"
echo "======================================"
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "✅ .env file already exists"
    read -p "Do you want to reconfigure it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing configuration"
        python3 send_gmail_report.py
        exit 0
    fi
fi

# Create .env from template
echo "Creating .env file..."
cp .env.example .env

echo ""
echo "📧 Gmail Configuration"
echo "====================="
echo ""
echo "You need to create an app-specific password for Gmail:"
echo ""
echo "1. Go to: https://myaccount.google.com/apppasswords"
echo "2. Make sure 2-Factor Authentication is enabled"
echo "3. Select 'Mail' and 'Windows Computer'"
echo "4. Copy the 16-character password"
echo ""

# Prompt for Gmail settings
read -p "Enter your Gmail address (sender): " gmail_sender
read -sp "Enter Gmail app password (16 chars, spaces will be removed): " gmail_app_password
echo ""

# Validate inputs
if [ -z "$gmail_sender" ] || [ -z "$gmail_app_password" ]; then
    echo "❌ Error: Gmail credentials are required"
    exit 1
fi

# Remove spaces from password
gmail_app_password=${gmail_app_password// /}

# Default recipient email
gmail_recipient="sathishkr.cs@gmail.com"
read -p "Recipient email (press Enter for default: $gmail_recipient): " custom_recipient
if [ -n "$custom_recipient" ]; then
    gmail_recipient="$custom_recipient"
fi

# Update .env file
cat > .env << EOF
# Gmail Configuration for Daily Reports
GMAIL_SENDER_EMAIL=$gmail_sender
GMAIL_APP_PASSWORD=$gmail_app_password
GMAIL_RECIPIENT_EMAIL=$gmail_recipient
EOF

echo ""
echo "✅ Configuration saved to .env"
echo ""
echo "Testing the setup..."
echo ""

# Run the validation and report script
python3 send_gmail_report.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup successful! Your report has been sent."
    echo ""
    echo "📅 Next Steps:"
    echo "1. Set up automation with one of these options:"
    echo ""
    echo "   Option A - Cron Job (Linux/Mac):"
    echo "   crontab -e"
    echo "   # Add: 0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> report_logs.txt 2>&1"
    echo ""
    echo "2. Or use GitHub Actions for automated daily reports"
    echo ""
    echo "Run this script anytime to regenerate reports or update settings."
else
    echo "❌ Setup failed. Please check your credentials and try again."
    exit 1
fi
