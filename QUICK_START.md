# Quick Start: Daily Repository Validation Reports

## 📌 Summary

Your repository is configured to automatically validate and send daily reports about:
- ✅ Repository integrity status
- 📊 New commits from the base branch (main) in the last 24 hours
- 📈 Branch information and uncommitted changes
- 📧 Professional HTML email reports

## 🚀 Quick Setup (5 minutes)

### Method 1: Automated Setup Script (Easiest)

```bash
chmod +x setup_daily_reports.sh
./setup_daily_reports.sh
```

The script will:
1. Create a `.env` configuration file
2. Prompt for your Gmail credentials
3. Test the setup by sending a report
4. Display next steps for automation

### Method 2: Manual Setup

#### Step 1: Enable Gmail 2-Factor Authentication
- Go to: https://myaccount.google.com/security
- Enable "2-Step Verification"

#### Step 2: Create App Password
- Go to: https://myaccount.google.com/apppasswords
- Select: Mail + Windows Computer
- Copy the 16-character password

#### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env and add:
# GMAIL_SENDER_EMAIL=your-email@gmail.com
# GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
# GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Test
```bash
python3 send_gmail_report.py
```

## 📅 Set Up Automation

### Option A: Cron Job (Linux/Mac)
```bash
crontab -e
# Add this line to run every day at 9 AM:
0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> report_logs.txt 2>&1
```

### Option B: GitHub Actions
The repository includes workflow templates in `.github/workflows/`

### Option C: Windows Task Scheduler
Create a scheduled task to run the Python script daily

## 📊 What You'll Receive

Each daily report includes:

| Item | Details |
|------|---------|
| Repository Name | x-devops |
| Current Branch | Your active working branch |
| Status | Clean working directory / Uncommitted changes |
| New Commits (24h) | List of all commits to main branch |
| Commit Info | Hash, Author, Date, Message |

### Example Report Content:
```
Repository: x-devops
Current Branch: claude/gifted-ride-s95hze
Uncommitted Changes: 0
New Commits (main, 24h): 5

Commits:
- 53ca98d John Doe - Daily AI concept 2026-06-08
- 4879c1e Jane Smith - Daily tweet 2026-06-07
- bc06121 John Doe - Daily tweet 2026-06-07
```

## 🔄 Run Reports On-Demand

Anytime you want to generate and send a report:
```bash
python3 send_gmail_report.py
```

## 🎯 Customization

You can customize:
- **Time Window**: Change from 24 hours to 7 days, 30 days, etc.
- **Recipients**: Add multiple recipient emails
- **Branches**: Include different branches in reports
- **Format**: Modify the HTML email template
- **Schedule**: Change automation frequency

Edit `send_gmail_report.py` to make these changes.

## 🆘 Troubleshooting

### "Email fails to send"
- ✓ Verify 2-Factor Authentication is enabled on Google account
- ✓ Check app password is correct (Gmail generates with spaces, you can remove them)
- ✓ Verify GMAIL_SENDER_EMAIL matches your Google account
- ✓ Check that .env file exists and has correct values
- ✓ Try signing into Gmail manually to verify account is accessible

### "Git fetch fails"
- ✓ Verify remote: `git remote -v`
- ✓ Check network connectivity
- ✓ Ensure you have repository access

### ".env file not found"
- ✓ Make sure you ran: `cp .env.example .env`
- ✓ Verify file exists in repository root: `ls -la .env`
- ✓ Check file permissions

## 📚 Additional Resources

- Full documentation: See `DAILY_REPORTS_SETUP.md`
- GitHub Actions setup: See `GITHUB_ACTIONS_SETUP.md`
- Python requirements: Check `requirements.txt`

## ✅ Status Checklist

- [ ] 2-Factor Authentication enabled on Google account
- [ ] App password created and copied
- [ ] .env file created and configured
- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] Test report sent successfully: `python3 send_gmail_report.py`
- [ ] Automation configured (cron/GitHub Actions/Task Scheduler)
- [ ] First daily report received

## 🎉 You're All Set!

Once you complete the setup, you'll receive daily repository validation reports automatically at your configured time.

---

**Questions?** Check the troubleshooting section above or review the detailed setup guide in `DAILY_REPORTS_SETUP.md`
