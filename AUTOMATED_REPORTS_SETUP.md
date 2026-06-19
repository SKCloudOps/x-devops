# Automated Daily Repository Reports via Gmail

This guide helps you set up daily repository validation reports sent to your Gmail using Claude Code's automation capabilities.

## What Gets Validated and Reported

✅ Repository name and current branch  
✅ Uncommitted changes count  
✅ New commits from main branch (last 24 hours)  
✅ Detailed commit list with author, date, and message  
✅ Professional HTML formatted email  

## Quick Start (5 minutes)

### Step 1: Configure Gmail Credentials

Edit `.env` file in the repository root:

```bash
# Edit the .env file
nano /home/user/x-devops/.env
```

Fill in your credentials:
```
GMAIL_SENDER_EMAIL=sathishkr.cs@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
```

### Step 2: Get Gmail App Password

**IMPORTANT:** You cannot use your regular Gmail password. You MUST generate an app-specific password:

1. Enable 2-Factor Authentication (if not already enabled):
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. Generate App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select: "Mail" and "Windows Computer"
   - Copy the generated 16-character password (remove spaces)
   - Paste into .env file as GMAIL_APP_PASSWORD

### Step 3: Test the Configuration

Run the setup verification:

```bash
python3 /home/user/x-devops/send_gmail_report.py
```

Expected output:
```
🔍 Starting repository validation and email sending...
📥 Fetching latest changes from remote...
✅ Validating repository...
============================================================
VALIDATION SUMMARY
============================================================
Repository: x-devops
Current Branch: claude/gifted-ride-joeb2i
Uncommitted Changes: 0
New Commits (main, 24h): [number]
============================================================
📧 Sending report to sathishkr.cs@gmail.com...
✅ Email sent successfully to sathishkr.cs@gmail.com
✅ Report sent successfully!
```

## Automation Options

### Option 1: Local Cron Job (Linux/Mac)

Set up daily reports using cron:

```bash
# Edit your crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> /home/user/x-devops/report_logs.txt 2>&1
```

View logs:
```bash
tail -f /home/user/x-devops/report_logs.txt
```

### Option 2: Claude Code Scheduled Routine

If running Claude Code on the web with scheduled routines enabled, create a recurring job:

```bash
# Run the setup script
/home/user/x-devops/setup_daily_reports.sh
```

This will:
- ✅ Verify .env configuration
- ✅ Check Python dependencies
- ✅ Test email sending
- ✅ Set up cron job for daily execution

### Option 3: GitHub Actions

Create `.github/workflows/daily-report.yml`:

```yaml
name: Daily Repository Report

on:
  schedule:
    - cron: '0 9 * * *'  # Run daily at 9 AM UTC
  workflow_dispatch:

jobs:
  validate-and-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run validation and send report
        env:
          GMAIL_SENDER_EMAIL: ${{ secrets.GMAIL_SENDER_EMAIL }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          GMAIL_RECIPIENT_EMAIL: ${{ secrets.GMAIL_RECIPIENT_EMAIL }}
        run: python3 send_gmail_report.py
```

Then add GitHub secrets:
- Go to Settings → Secrets and variables → Actions
- Add: GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD, GMAIL_RECIPIENT_EMAIL

## Files Overview

| File | Purpose |
|------|---------|
| `send_gmail_report.py` | Main script - validates repo and sends email |
| `validate_and_report.py` | Validation logic and HTML report generation |
| `send_validation_report.py` | Alternative validation reporter |
| `.env` | Configuration file (NOT committed to git) |
| `.env.example` | Template for .env file |
| `requirements.txt` | Python dependencies |
| `setup_daily_reports.sh` | Setup automation script |

## Email Report Format

The HTML email includes:

```
📋 Repository Validation Report
Generated: [timestamp]

📌 Repository Info
├─ Repository: x-devops
└─ Current Branch: claude/gifted-ride-joeb2i

📊 Repository Status
└─ Uncommitted Changes: 0
└─ Status: Clean working directory

📈 Changes from Main Branch (Last 24 Hours)
└─ Total New Commits: [number]
└─ [Detailed commit table with hash, author, date, message]
```

## Troubleshooting

### Email sends but arrives in spam

1. Gmail may mark initial emails as suspicious
2. Mark it as "Not Spam" in Gmail
3. Add sender to contacts
4. Gmail will learn and deliver to inbox on future sends

### "SMTPAuthenticationError"

Check:
- ✓ GMAIL_SENDER_EMAIL is correct and has 2FA enabled
- ✓ GMAIL_APP_PASSWORD is the app password (not regular password)
- ✓ App password has no spaces (remove them if generated with spaces)
- ✓ App password hasn't been revoked

To revoke and regenerate:
1. Go to: https://myaccount.google.com/apppasswords
2. Delete the old password
3. Generate a new one

### Script can't find .env file

```bash
# Verify .env exists in repo root
ls -la /home/user/x-devops/.env

# Verify it's readable
cat /home/user/x-devops/.env
```

### Git errors

```bash
# Verify remote is accessible
git remote -v

# Check network connectivity
ping github.com
```

## Security Notes

⚠️ **IMPORTANT:**
- ✓ Never commit `.env` file (it's in `.gitignore`)
- ✓ Never share your Gmail app password
- ✓ The app password only works for Gmail
- ✓ You can revoke it anytime in Google account settings
- ✓ App password is less secure than 2FA, so keep it safe

## Customization

Edit `send_gmail_report.py` to:
- Change the days window for commits (line 30: `days=1`)
- Modify the HTML email template (lines 85-149)
- Add additional validation checks
- Include different branches in the report
- Add multiple recipient emails

Example - change to 7-day report:
```python
# Line 30 in send_gmail_report.py
main_commits = get_git_log(days=7, branch="main")
```

## Manual Test

Test sending a report without automation:

```bash
cd /home/user/x-devops

# Validate and show report
python3 validate_and_report.py

# Validate and send email
python3 send_gmail_report.py
```

## Support

For issues:
1. Check the troubleshooting section above
2. Verify all setup steps are completed
3. Review the validation output for specific errors
4. Check log files in `/home/user/x-devops/report_logs.txt`

## Next Steps

1. ✅ Edit `.env` with your Gmail credentials
2. ✅ Test with: `python3 send_gmail_report.py`
3. ✅ Set up automation (cron, GitHub Actions, or Claude Code routine)
4. ✅ Monitor the first few reports to ensure they arrive

Enjoy automated daily repository reports! 📊
