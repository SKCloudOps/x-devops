#!/bin/bash

# Setup script for daily repository validation reports
# This script guides you through the setup process

set -e

echo "=================================================="
echo "🔧 Daily Repository Validation Report Setup"
echo "=================================================="
echo ""

# Step 1: Check Python installation
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
echo "✅ Python 3 is installed: $(python3 --version)"
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing required dependencies..."
pip3 install -q -r requirements.txt
echo "✅ Dependencies installed successfully"
echo ""

# Step 3: Create .env file if it doesn't exist
echo "Step 3: Setting up Gmail configuration..."
if [ -f ".env" ]; then
    echo "ℹ️  .env file already exists"
    echo "To reconfigure, delete .env and run this script again"
else
    echo ""
    echo "📝 You need to create a .env file with Gmail credentials."
    echo "Follow these steps:"
    echo ""
    echo "1️⃣  Go to https://myaccount.google.com/security"
    echo "    - Enable 2-Step Verification (if not already enabled)"
    echo ""
    echo "2️⃣  Go to https://myaccount.google.com/apppasswords"
    echo "    - Select 'Mail' and 'Windows Computer'"
    echo "    - Google will generate a 16-character password"
    echo "    - Copy this password (you can remove spaces)"
    echo ""
    echo "3️⃣  Enter your Gmail configuration below:"
    echo ""

    read -p "Enter your Gmail address (sender): " SENDER_EMAIL
    read -sp "Enter your Gmail app password (16 chars, spaces removed): " APP_PASSWORD
    echo ""
    read -p "Enter recipient email (press Enter for sathishkr.cs@gmail.com): " RECIPIENT_EMAIL
    RECIPIENT_EMAIL=${RECIPIENT_EMAIL:-sathishkr.cs@gmail.com}

    # Create .env file
    cat > .env << EOF
# Gmail Configuration for Daily Reports
GMAIL_SENDER_EMAIL=$SENDER_EMAIL
GMAIL_APP_PASSWORD=$APP_PASSWORD
GMAIL_RECIPIENT_EMAIL=$RECIPIENT_EMAIL
EOF

    echo ""
    echo "✅ .env file created successfully"
fi
echo ""

# Step 4: Test the setup
echo "Step 4: Testing repository validation and email..."
echo ""
python3 send_gmail_report.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ Setup completed successfully!"
    echo "=================================================="
    echo ""
    echo "📧 Check your email for the validation report."
    echo ""
    echo "Next steps for automation:"
    echo ""
    echo "Option A - Schedule with Cron (Linux/Mac):"
    echo "  crontab -e"
    echo "  Add: 0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> report_logs.txt 2>&1"
    echo "  (This runs daily at 9 AM)"
    echo ""
    echo "Option B - Use GitHub Actions:"
    echo "  See GITHUB_ACTIONS_SETUP.md for instructions"
    echo ""
else
    echo ""
    echo "❌ Setup test failed. Please check the error messages above."
    exit 1
fi
