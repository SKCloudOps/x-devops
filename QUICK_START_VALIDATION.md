# Quick Start: Daily Repository Validation & Email Reports

Your automated daily repository validation and email reporting system is now set up! Here's how to use it.

## 🚀 What You Get

✅ **Automated Daily Reports** - Repository validation runs every day at 9 AM UTC  
✅ **Email Integration** - Reports sent to your Gmail inbox  
✅ **Complete Validation** - Commits, branches, file changes, health checks  
✅ **Flexible Scheduling** - GitHub Actions or local cron jobs  
✅ **Beautiful Reports** - HTML-formatted emails with detailed insights  

## 📋 What Gets Reported

Each daily report includes:
- ✓ Repository status (clean working directory?)
- ✓ New commits in the last 24 hours
- ✓ Comparison with base branch (ahead/behind commits)
- ✓ File changes in the last 24 hours
- ✓ Git repository health (dangling objects, integrity)

## 🎯 Quick Setup (Choose One)

### Option A: Use GitHub Actions (Recommended)

**Already set up!** The workflow in `.github/workflows/daily-validation-report.yml` will:
- Run automatically every day at 9 AM UTC
- Generate validation reports
- Upload artifacts for safekeeping
- Create workflow summaries

**To verify it's working:**
1. Go to your repository → Actions tab
2. Look for "Daily Repository Validation Report"
3. Click to see the workflow runs
4. Check the latest run for the report output

**To trigger manually:**
```bash
gh workflow run daily-validation-report.yml
```

### Option B: Use Local Cron Job

**Setup (one-time):**
```bash
bash scripts/setup-cron.sh
```

This will guide you through creating a cron job that runs daily.

## 📧 Sending Reports to Gmail

### Method 1: Using GitHub Actions (Automated)

The GitHub Actions workflow generates email payloads. You can:
1. View the payload in workflow run logs
2. Use Claude Code with Gmail MCP tools to send
3. Set up additional automation in GitHub Actions

### Method 2: Manual Report Generation

Generate a report anytime:

```bash
# Generate validation report
bash scripts/validate_and_report.sh

# View the report
cat /tmp/repo_validation_report.txt

# Prepare email payload
REPORT_EMAIL="your-email@gmail.com" python3 scripts/send_daily_report.py
```

### Method 3: Send with Claude Code

```bash
# Using Claude Code's Gmail integration
python3 scripts/send_daily_report.py --email your-email@gmail.com

# Then use Claude Code to send the draft:
# - Use the payload from the previous command
# - Create a Gmail draft with mcp__Gmail__create_draft
# - Send the email
```

## ⚙️ Customization

### Change Daily Run Time

Edit `.github/workflows/daily-validation-report.yml`:

```yaml
schedule:
  - cron: '0 18 * * *'  # Change to 6 PM UTC
```

Cron format: `minute hour * * *`
- `0 9 * * *` = 9 AM daily
- `0 18 * * *` = 6 PM daily  
- `0 9 * * 1` = Every Monday at 9 AM

### Change Report Email Recipient

Add to GitHub Secrets:
1. Settings → Secrets and variables → Actions
2. Create new secret: `REPORT_EMAIL` = `your-email@gmail.com`

Or use environment variable:
```bash
export REPORT_EMAIL="your-email@gmail.com"
python3 scripts/send_daily_report.py
```

### Change Base Branch for Comparison

Set `BASE_BRANCH` before running:
```bash
BASE_BRANCH="develop" bash scripts/validate_and_report.sh
```

Or edit the scripts to change the default.

## 📁 Files Overview

```
x-devops/
├── VALIDATION_REPORT_SETUP.md          # Detailed setup guide
├── QUICK_START_VALIDATION.md           # This file
├── .github/workflows/
│   └── daily-validation-report.yml    # GitHub Actions workflow
└── scripts/
    ├── README.md                       # Scripts documentation
    ├── validate_and_report.sh          # Validation script
    ├── send_daily_report.py            # Email generator
    └── setup-cron.sh                   # Cron setup helper
```

## 🔍 Understanding the Reports

### Example Report Section

```
=== New Commits (last 24 hours) ===
Found 3 new commit(s):

a1b2c3d | Jane Doe | Add feature X | 2 hours ago
d4e5f6g | John Smith | Fix bug Y | 5 hours ago
```

### Status Indicators

- ✓ Everything is good
- ⚠ Warning or issue found (e.g., uncommitted changes)
- ❌ Error condition

### Key Metrics

- **Commits ahead of base** - How many commits on your branch not in main
- **Commits behind base** - How many commits in main not on your branch
- **Files modified** - How many files changed in last 24 hours
- **Dangling objects** - Git integrity issues (usually harmless)

## 🆘 Troubleshooting

### Report not generating?
```bash
# Test manually
bash scripts/validate_and_report.sh
cat /tmp/repo_validation_report.txt
```

### Email not sending?
- Verify email address: `echo $REPORT_EMAIL`
- Check Gmail API is enabled in your Google account
- Ensure Gmail MCP tools are available in Claude Code

### Cron job not running?
```bash
# Check if installed
crontab -l

# Check logs
tail -f /var/log/repo-validation-*.log
```

### Scripts not executable?
```bash
chmod +x scripts/*.sh scripts/*.py
```

## 📚 Full Documentation

For detailed information, see:
- **VALIDATION_REPORT_SETUP.md** - Complete setup guide
- **scripts/README.md** - Script documentation
- **workflows/daily-validation-report.yml** - GitHub Actions workflow

## 💡 Tips & Tricks

1. **Add to Dashboard**: Screenshot the report and add to team dashboard
2. **Integrate with Slack**: Add GitHub Actions to Slack notifications
3. **Custom Checks**: Edit `validate_and_report.sh` to add custom validations
4. **Email Automation**: Use Gmail labels/filters to organize reports
5. **Team Reports**: Create a shared email for team distribution lists

## 🎓 Learn More

- Git cron format: https://crontab.guru
- GitHub Actions: https://docs.github.com/en/actions
- Gmail API: https://developers.google.com/gmail/api
- Claude Code: https://claude.ai/code

## 🎉 You're All Set!

Your automated validation and reporting system is ready to use. 

**Next steps:**
1. ✅ Check that GitHub Actions workflow runs tomorrow morning
2. ✅ Set up email delivery (GitHub Actions or manual)
3. ✅ Customize as needed for your team

Questions? Check the documentation files or review the script comments for more details.
