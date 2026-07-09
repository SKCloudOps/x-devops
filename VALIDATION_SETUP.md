# Daily Repository Validation & Email Reports Setup

This guide helps you set up automated daily repository validation and email reports for the x-devops repository.

## 📋 What's Configured

✅ **Repository Validation**
- Checks for uncommitted changes
- Analyzes new commits from the main branch (last 24 hours)
- Analyzes commits from current branch (last 7 days)
- Professional HTML-formatted reports

✅ **Automated Daily Schedule**
- Daily cron job scheduled at **9:03 AM UTC**
- Runs: `/home/user/x-devops/validate_and_send_report.py`
- Auto-expires after 7 days (session-only, for this Claude session)

✅ **Email Report Features**
- Repository status summary
- Uncommitted changes count
- Detailed commit history from main branch
- Current branch activity
- Professional HTML formatting

---

## 🚀 Current Setup Status

### ✅ Completed
- [x] Validation script created: `validate_and_send_report.py`
- [x] Daily cron job scheduled (Job ID: 47814ae2)
- [x] Script tested and working
- [x] Recipient configured: **sathishkr.cs@gmail.com**

### Test Results
```
Repository: x-devops
Current Branch: claude/gifted-ride-2kepz5
Uncommitted Changes: 1
New Commits (main, 24h): 0
Status: ✅ Ready
```

---

## 📧 Receiving Email Reports

### Option 1: Gmail MCP Server (Recommended for Claude Sessions)
If you're running this within Claude Code:
1. The validation runs automatically daily at 9:03 AM UTC
2. Reports are prepared in HTML format
3. You'll receive notifications when the routine completes

### Option 2: Gmail SMTP (For External Automation)
If you want to send emails outside of Claude:

**Step 1: Set up Gmail App Password**
1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to: https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows Computer"
5. Copy the 16-character app password

**Step 2: Create .env file**
```bash
cp /home/user/x-devops/.env.example /home/user/x-devops/.env
```

**Step 3: Edit .env**
```
GMAIL_SENDER_EMAIL=sathishkr.cs@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
```

**Step 4: Test (Optional)**
```bash
cd /home/user/x-devops
python3 send_gmail_report.py
```

---

## 🛠️ Available Scripts

### 1. validate_and_send_report.py (NEW - Recommended)
Complete validation and report generation:
```bash
python3 validate_and_send_report.py
```

**Output:**
- Validation summary with uncommitted changes
- New commits from main branch (24h)
- Commits from current branch (7d)
- Professional HTML report
- JSON backup of report data

### 2. send_gmail_report.py (Original)
Uses Gmail SMTP (requires .env configuration):
```bash
python3 send_gmail_report.py
```

### 3. send_validation_report.py (Original)
Generates validation report (no email sending):
```bash
python3 send_validation_report.py
```

---

## 📅 Daily Automation

### How It Works
1. **Cron Job Triggers**: Every day at 9:03 AM UTC
2. **Validation Runs**: `validate_and_send_report.py` executes
3. **Fetches Updates**: `git fetch origin` pulls latest changes
4. **Analyzes Changes**: Checks commits and status
5. **Generates Report**: HTML-formatted report is created
6. **Report Data Saved**: JSON backup for reference

### Manual Runs
You can manually run validation anytime:
```bash
cd /home/user/x-devops
python3 validate_and_send_report.py
```

---

## 📊 Report Contents

Each daily report includes:

**Repository Information**
- Repository name: x-devops
- Current branch: claude/gifted-ride-2kepz5
- Remote URL

**Repository Status**
- Uncommitted changes count
- Details of modified/untracked files (if any)

**Main Branch Activity (Last 24 Hours)**
- Number of new commits
- List of commits with:
  - Commit hash (short form)
  - Author name
  - Commit date
  - Commit message

**Current Branch Activity (Last 7 Days)**
- Number of commits on your current branch
- Details of recent commits

---

## 🔧 Customization

### Change Daily Schedule Time
Edit cron expression to run at different time:
- `0 8 * * *` = 8:00 AM UTC
- `0 9 * * *` = 9:00 AM UTC (default, but slightly delayed)
- `0 14 * * *` = 2:00 PM UTC
- `0 0 * * *` = Midnight UTC

### Change Report Recipients
Edit `validate_and_send_report.py`:
```python
recipient_email = "your-email@gmail.com"
```

### Extend Commit History Window
Modify the days parameter in `get_git_log()`:
```python
main_commits = get_git_log(days=7, branch="main")  # Show 7 days instead of 1
```

### Add Additional Branches to Monitor
Extend the `validate_repository()` function to add more branch checks

---

## 🐛 Troubleshooting

### Email Not Sending (SMTP Method)
1. Verify 2-factor authentication is enabled on Google account
2. Verify app password is correct (16 characters, spaces can be removed)
3. Check that GMAIL_SENDER_EMAIL matches the account you created the app password for
4. Ensure .env file is in the correct location: `/home/user/x-devops/.env`

### Script Not Finding .env
- Check file exists: `ls -la /home/user/x-devops/.env`
- Check permissions: `chmod 600 /home/user/x-devops/.env`

### Cron Job Not Running
- Verify cron service is running: `crontab -l` (for manual setup)
- Check logs: `tail -f /var/log/syslog | grep CRON`
- For this Claude session: Job runs while Claude is idle

### Git Fetch Fails
- Check internet connectivity
- Verify remote is accessible: `git remote -v`
- Check repository permissions

---

## 📋 Security Notes

⚠️ **Important for SMTP Method:**
- **DO NOT** commit the `.env` file (it's in `.gitignore`)
- **DO NOT** share your Gmail app password
- The app password only works for Gmail, not other Google services
- You can revoke the app password anytime in your Google account settings
- Never use your main Gmail password, always use the app-specific password

✅ **Best Practices:**
- Keep `.env` file in `.gitignore`
- Review uncommitted changes regularly
- Monitor the report for unexpected changes
- Keep your Gmail account secure with 2FA enabled

---

## 📚 Additional Resources

- [Gmail App Passwords](https://myaccount.google.com/apppasswords)
- [Gmail Security](https://myaccount.google.com/security)
- [Repository Documentation](README.md)
- [GitHub Actions Setup](GITHUB_ACTIONS_SETUP.md)

---

## 🎯 Next Steps

1. **Choose Email Method:**
   - Claude sessions: Reports prepared, use Gmail MCP for sending
   - External automation: Set up `.env` with SMTP credentials

2. **Monitor First Report:**
   - Check your email tomorrow at ~9:03 AM UTC
   - Verify format and content

3. **Customize as Needed:**
   - Adjust schedule time
   - Change recipients
   - Modify report content

4. **Set Up Persistent Automation (Optional):**
   - For permanent cron on Linux: `crontab -e`
   - For GitHub Actions: Use `.github/workflows/daily-report.yml`
   - For Cloud Services: Google Cloud Scheduler, AWS Lambda, etc.

---

## 📞 Support

For issues:
1. Run validation manually: `python3 validate_and_send_report.py`
2. Check output for errors
3. Verify all configuration is correct
4. Review troubleshooting section above

---

**Last Updated:** July 9, 2026
**Setup Status:** ✅ Complete and Testing
**Next Report:** Tomorrow at ~9:03 AM UTC
