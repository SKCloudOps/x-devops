# Complete Setup Guide - Daily Repository Validation Reports

## Overview
This setup enables automated daily repository validation reports sent to your Gmail inbox. Reports include:
- Repository status and branch information
- Uncommitted changes count
- New commits from the base branch (last 24 hours)
- Detailed commit information (hash, author, date, message)

## Your Email
**Recipient Email:** sathishkr.cs@gmail.com

---

## Step 1: Enable Gmail Authentication

### 1a. Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification" section
3. Click "Enable" and follow the prompts
4. Verify your phone number and set up authentication method

### 1b. Create App-Specific Password
1. Once 2FA is enabled, go to: https://myaccount.google.com/apppasswords
2. Select:
   - **App:** Mail
   - **Device:** Windows Computer (or any device)
3. Click "Generate"
4. Google will display a 16-character password (format: `xxxx xxxx xxxx xxxx`)
5. **Copy this password** - you'll need it in the next step

---

## Step 2: Create .env Configuration File

1. Create `.env` file in the repository root (`/home/user/x-devops/.env`)
2. Add the following content:

```
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
```

3. Replace:
   - `your-email@gmail.com` with your actual Gmail address
   - `xxxx xxxx xxxx xxxx` with the 16-character password from Step 1b
   - Keep `GMAIL_RECIPIENT_EMAIL` as is (it will send to sathishkr.cs@gmail.com)

**Example:**
```
GMAIL_SENDER_EMAIL=john.doe@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
```

---

## Step 3: Test the Setup

Run the validation and report script:

```bash
cd /home/user/x-devops
python3 send_gmail_report.py
```

**Expected Output:**
```
🔍 Starting repository validation and email sending...
📥 Fetching latest changes from remote...
✅ Validating repository...
============================================================
VALIDATION SUMMARY
============================================================
Repository: x-devops
Current Branch: claude/gifted-ride-re59d8
Uncommitted Changes: 0
New Commits (main, 24h): X
============================================================
📧 Sending report to sathishkr.cs@gmail.com...
✅ Email sent successfully to sathishkr.cs@gmail.com
✅ Report sent successfully!
```

---

## Step 4: Set Up Daily Automation

Choose one of the following methods:

### Option A: Linux/Mac Cron Job (Recommended for local environments)

1. Open crontab editor:
```bash
crontab -e
```

2. Add this line to run daily at 9 AM UTC:
```
0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> /home/user/x-devops/report_logs.txt 2>&1
```

3. Adjust time as needed:
   - `0 9` = 9 AM UTC (change first `9` to different hour: 0-23)
   - `* * *` = Every day, month, day of week

4. Verify cron is set:
```bash
crontab -l
```

### Option B: GitHub Actions (Recommended for cloud environments)

The repository already has a workflow template. To enable it:

1. Go to GitHub repository Settings → Secrets and variables → Actions
2. Add these secrets:
   - `GMAIL_SENDER_EMAIL`: Your Gmail address
   - `GMAIL_APP_PASSWORD`: Your 16-character app password
   - `GMAIL_RECIPIENT_EMAIL`: sathishkr.cs@gmail.com

3. The workflow `.github/workflows/daily-report.yml` will automatically run daily

---

## Troubleshooting

### Email fails to send
- ✓ Verify app password has no spaces (or all spaces - both work)
- ✓ Confirm 2-factor authentication is enabled
- ✓ Ensure GMAIL_SENDER_EMAIL matches your Gmail account
- ✓ Check that .env file is in `/home/user/x-devops/.env`
- ✓ Try manually logging into Gmail to verify account is active

### Script can't find .env file
- Ensure `.env` file exists in `/home/user/x-devops/`
- Check file permissions: `ls -la .env`
- Verify no typos in filename

### Cron job not running
- Check crontab is set: `crontab -l`
- Verify script path is correct
- Check logs: `tail -f /home/user/x-devops/report_logs.txt`
- Test manually: `cd /home/user/x-devops && python3 send_gmail_report.py`

### Repository validation errors
- Ensure git remote is accessible: `git remote -v`
- Check network connectivity: `ping google.com`
- Verify main branch exists: `git branch -a`

---

## Report Contents

Each daily report includes:

**Repository Information:**
- Repository name
- Current working branch
- Remote URL

**Repository Status:**
- Uncommitted changes count
- Clean/dirty working tree status

**Changes from Main Branch (Last 24 Hours):**
- Total number of new commits
- Detailed commit table with:
  - Commit hash (short)
  - Author name
  - Commit date
  - Commit message

---

## Security Notes

⚠️ **Important:**
- Never commit the `.env` file (it's in `.gitignore`)
- Never share your Gmail app password
- The app password ONLY works for Gmail, not other Google services
- You can revoke app passwords anytime: https://myaccount.google.com/apppasswords

---

## Customization

Edit `send_gmail_report.py` to customize:
- **Report frequency**: Change `days=1` in `get_git_log()` (1=24h, 7=weekly, 30=monthly)
- **Email schedule**: Modify cron time or GitHub Actions trigger
- **Branches monitored**: Change `branch="main"` to monitor different branches
- **Report format**: Edit HTML template in `format_html_report()`
- **Additional recipients**: Modify email sending section

---

## Next Steps

1. ✅ Enable 2-Factor Authentication (if not already enabled)
2. ✅ Generate Gmail App Password
3. ✅ Create `.env` file with credentials
4. ✅ Test with: `python3 send_gmail_report.py`
5. ✅ Set up automation (cron job or GitHub Actions)
6. ✅ Receive daily reports in your inbox!

---

**Questions or Issues?**
- Review the Troubleshooting section above
- Check original documentation: `DAILY_REPORTS_SETUP.md`
- Review script output for specific errors
