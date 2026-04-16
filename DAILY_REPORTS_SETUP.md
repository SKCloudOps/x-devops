# Daily Repository Validation Reports Setup

This guide helps you set up automated daily validation reports sent to your Gmail.

## What's Included

- **validate_and_report.py** - Validates repository integrity and generates HTML reports
- **send_validation_report.py** - Generates reports in email-ready format
- **send_gmail_report.py** - Sends reports via Gmail SMTP
- **requirements.txt** - Required Python packages (includes python-dotenv)

## Reports Include

✅ Repository name and current branch
✅ Uncommitted changes count
✅ New commits from main branch (last 24 hours)
✅ Detailed commit list with hash, author, date, and message
✅ Professional HTML formatted email

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Gmail Authentication

**Important:** You need to use an app-specific password, not your regular Gmail password.

#### 2a. Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

#### 2b. Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Google will generate a 16-character password
4. Copy this password (it will have spaces, you can remove them)

#### 2c. Create .env File
1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   GMAIL_SENDER_EMAIL=your-email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   GMAIL_RECIPIENT_EMAIL=sathishkrcs@gmail.com
   ```

3. **Important:** The `.env` file is in `.gitignore` and will not be committed

### Step 3: Test the Setup

```bash
python3 send_gmail_report.py
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
Current Branch: claude/gifted-ride-QEH2a
Uncommitted Changes: 0
New Commits (main, 24h): 19
============================================================
📧 Sending report to sathishkrcs@gmail.com...
✅ Email sent successfully to sathishkrcs@gmail.com
✅ Report sent successfully!
```

## Automation Options

### Option 1: Cron Job (Linux/Mac)

Create a daily cron job to run the report at 9 AM:

```bash
# Edit crontab
crontab -e

# Add this line (runs every day at 9 AM)
0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> /home/user/x-devops/report_logs.txt 2>&1
```

### Option 2: GitHub Actions

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
      - uses: actions/checkout@v3
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

### Option 3: Manual Cloud Scheduler

Using Google Cloud Scheduler or similar services to trigger the script periodically.

## Troubleshooting

### Email fails to send
- Verify app password is correct (remove any spaces)
- Ensure 2-factor authentication is enabled on Google account
- Check that GMAIL_SENDER_EMAIL matches your app password account
- Try logging in to Gmail to verify the account is active

### Script can't find .env file
- Ensure `.env` file is in the repository root (`/home/user/x-devops/.env`)
- Check file permissions

### Git fetch fails
- Verify remote is accessible: `git remote -v`
- Check network connectivity

## Example Report

The email will contain:
- Repository name: x-devops
- Current branch information
- Uncommitted changes status
- List of new commits on main branch from the last 24 hours
- Each commit shows: hash, author, date, and commit message

## Customization

You can modify the scripts to:
- Change the commit history window (days: 1, 7, 30, etc.)
- Add additional validation checks
- Modify the HTML report format
- Add multiple recipient emails
- Include different branches in the report

## Security Notes

⚠️ **Important:**
- Never commit the `.env` file (it's in `.gitignore`)
- Never share your Gmail app password
- The app password only works for Gmail, not other Google services
- You can revoke the app password anytime in your Google account settings

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all setup steps are completed correctly
3. Run the test command to check configuration
