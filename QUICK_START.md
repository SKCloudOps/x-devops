# 🚀 Quick Start: Daily Repository Validation Reports

Your repository is ready to send automated validation reports to your Gmail! Choose one of the following setup options.

## What You'll Get

Each daily report includes:
- ✅ Repository validation status
- ✅ Current branch information  
- ✅ Uncommitted changes count
- ✅ New commits from the base branch (main) in the last 24 hours
- ✅ Detailed commit list with hash, author, date, and message
- ✅ Professional HTML formatted email

---

## 📋 Option 1: Local Setup (Recommended for Testing)

Perfect for testing locally or if you want to run reports on your machine.

### Quick Setup (2 minutes)

```bash
# Navigate to the repository
cd /home/user/x-devops

# Run the automated setup script
./setup_daily_reports.sh
```

The script will:
1. ✅ Check Python installation
2. ✅ Install dependencies
3. ✅ Guide you through Gmail configuration
4. ✅ Test the system with a sample report

### Manual Setup Steps

If you prefer to set it up manually:

#### Step 1: Install Dependencies
```bash
pip3 install -r requirements.txt
```

#### Step 2: Create .env File
```bash
cp .env.example .env
```

Edit `.env` with your Gmail credentials:
```
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
```

#### Step 3: Get Gmail App Password

⚠️ **Important:** Use an app-specific password, NOT your regular Gmail password!

1. Go to https://myaccount.google.com/security
   - Enable 2-Step Verification (if not already enabled)

2. Go to https://myaccount.google.com/apppasswords
   - Select "Mail" from dropdown
   - Select "Windows Computer" from device dropdown  
   - Click "Generate"
   - Copy the 16-character password

3. Paste the password into `.env`

#### Step 4: Test It
```bash
python3 send_gmail_report.py
```

You should see:
```
🔍 Starting repository validation and email sending...
📥 Fetching latest changes from remote...
✅ Validating repository...
============================================================
VALIDATION SUMMARY
============================================================
Repository: x-devops
Current Branch: claude/gifted-ride-Fghaa
Uncommitted Changes: X
New Commits (main, 24h): X
============================================================
📧 Sending report to sathishkr.cs@gmail.com...
✅ Email sent successfully to sathishkr.cs@gmail.com
✅ Report sent successfully!
```

### Schedule with Cron (Linux/Mac)

To run the report daily at 9 AM:

```bash
# Open crontab editor
crontab -e

# Add this line (runs every day at 9 AM)
0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> report_logs.txt 2>&1
```

Check logs:
```bash
tail -f report_logs.txt
```

---

## ☁️ Option 2: GitHub Actions (Recommended for Production)

Fully automated, no local setup needed. Reports run in the cloud every day.

### Setup in 5 Minutes

#### Step 1: Get Gmail App Password

Same as above:
1. Go to https://myaccount.google.com/apppasswords
2. Generate password for "Mail" / "Windows Computer"
3. Copy the 16-character password

#### Step 2: Add GitHub Secrets

1. Go to: https://github.com/SKCloudOps/x-devops/settings/secrets/actions

2. Click "New repository secret" and add these three:

| Name | Value |
|------|-------|
| `GMAIL_SENDER_EMAIL` | Your Gmail address (e.g., `sathishkr.cs@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-char password from Step 1 |
| `GMAIL_RECIPIENT_EMAIL` | `sathishkr.cs@gmail.com` |

#### Step 3: Verify Workflow

1. Go to **Actions** tab on GitHub
2. You should see "Daily Repository Validation Report"
3. The workflow will run automatically daily at 9 AM UTC

#### Step 4: Manual Test

To test immediately (don't wait 24 hours):

1. Go to **Actions** tab
2. Select "Daily Repository Validation Report"
3. Click "Run workflow" → "Run workflow"
4. Watch the logs in real-time

---

## 📧 Troubleshooting

### Email fails to send

**Check:**
1. Verify app password is correct (remove any spaces)
2. Ensure 2-factor authentication is enabled on Google account
3. Verify `GMAIL_SENDER_EMAIL` matches your app password account
4. Check .env file exists in repository root (local setup)

### Script can't find .env file

- Make sure `.env` is in `/home/user/x-devops/.env`
- Verify file permissions: `ls -la .env`

### Git fetch fails

- Check remote access: `git remote -v`
- Verify network connectivity

### No email received

1. Check Gmail spam/promotions folders
2. Verify sender email is correct
3. Check script output for error messages
4. Try re-running the test command

---

## 🔧 Customization

You can modify the scripts to:
- Change commit history window (currently 1 day, configurable to 7, 30, etc.)
- Add additional validation checks
- Modify HTML report format
- Add multiple recipient emails
- Include different branches in reports

See the comments in `send_gmail_report.py` for customization details.

---

## 🔐 Security Notes

⚠️ **Important:**
- Never commit the `.env` file (it's in `.gitignore`)
- Never share your Gmail app password
- The app password only works for Gmail
- You can revoke the app password anytime at https://myaccount.google.com/apppasswords

---

## 📁 Files Included

- `send_gmail_report.py` - Main script for validation and email
- `validate_and_report.py` - Validation logic
- `setup_daily_reports.sh` - Automated setup helper
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template
- `DAILY_REPORTS_SETUP.md` - Detailed setup guide
- `GITHUB_ACTIONS_SETUP.md` - GitHub Actions guide

---

## 🎯 Next Steps

1. Choose Option 1 (Local) or Option 2 (GitHub Actions)
2. Follow the setup steps above
3. Test with a manual run
4. Check your Gmail for the report
5. Monitor automated runs going forward

**Questions?** See the detailed guides in:
- `DAILY_REPORTS_SETUP.md` - Local setup details
- `GITHUB_ACTIONS_SETUP.md` - GitHub Actions details

---

## ✅ Recent Test Run

```
Repository: x-devops
Current Branch: claude/gifted-ride-Fghaa
Uncommitted Changes: 0
New Commits (main, 24h): 8
Status: ✅ Ready to send reports
```

You're all set! Start your preferred setup option above. 🎉
