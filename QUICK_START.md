# Quick Start Guide - Daily Repository Validation & Gmail Reports

## ✅ Setup Complete!

Your automated daily repository validation and Gmail reporting system is now active.

## What's Been Set Up

### 1. **Automated Daily Validation**
- Runs automatically **every day at 9:15 AM**
- Checks repository status, commits, and changes
- Generates comprehensive HTML-formatted reports
- Sends reports to your Gmail as drafts

### 2. **Validation Scripts**
```
/home/user/x-devops/
├── daily-validation.sh    → Core validation engine
├── daily-report.sh        → Master orchestration script
└── send-report.py         → Report helper
```

### 3. **Gmail Integration**
- **Email:** sathishkr.cs@gmail.com
- **Report Type:** HTML formatted with tables, colors, and statistics
- **Frequency:** Daily at 9:15 AM
- **Status:** Drafts created automatically (ready to send)

## What Gets Validated

Each daily report includes:
✓ Repository accessibility check  
✓ Remote configuration verification  
✓ Current branch status  
✓ New commits in base branch (last 24h)  
✓ Commits ahead of base branch  
✓ Uncommitted changes detection  
✓ Latest commit history  
✓ Overall repository health summary  

## Quick Commands

### Test the full workflow immediately:
```bash
bash /home/user/x-devops/daily-report.sh
```

### View the latest report:
```bash
cat /tmp/latest-repo-report.txt
```

### Check validation logs:
```bash
cat /tmp/repo-validation-$(date +%Y%m%d).log
```

### View recent reports:
```bash
ls -lt /tmp/repo-report-*.txt | head -5
```

## Viewing Your Reports

1. **Open Gmail**
2. **Go to Drafts folder**
3. **Look for:** "Daily Repository Validation Report - x-devops"
4. **Each morning:** New draft will be created at 9:15 AM
5. **Review:** Check status, commits, and health metrics
6. **Send (optional):** Review and send the draft or discard

## Report Example

Your daily email will include:
- Repository status and branch information
- New commits table with hashes and messages
- Validation check results (all passed or issues highlighted)
- Uncommitted files list
- Summary statistics
- Next scheduled run time

## Important Notes

⚠️ **Session-Only Job:**
- The automated job runs while the Claude Code session is active
- Job auto-expires after 7 days of continuous operation
- For persistent scheduling beyond 7 days, the job can be renewed

📧 **Gmail Integration:**
- Uses Gmail MCP tools to create draft emails
- Drafts are created automatically each day
- You can review, modify, and send them manually
- Or set up automatic sending with additional configuration

## Customization

### Change recipient email:
Edit `/home/user/x-devops/daily-validation.sh` and update `RECIPIENT_EMAIL`

### Change schedule time:
Delete current job and create new one with different time:
- Current: 9:15 AM (`15 9 * * *`)
- Alternatives:
  - 8:00 AM: `0 8 * * *`
  - 12:00 PM: `0 12 * * *`
  - 6:00 PM: `0 18 * * *`

### Add more validation checks:
Edit `/home/user/x-devops/daily-validation.sh` and add git commands or custom checks

## Troubleshooting

**No draft appearing in Gmail?**
- Check Gmail Drafts folder (not Inbox)
- Verify email address is correct
- Check browser is refreshed

**Scripts not running?**
- Ensure scripts have execute permissions: `chmod +x *.sh`
- Check `/tmp/repo-validation-*.log` for errors
- Verify git repository is accessible

**Want to test manually right now?**
```bash
bash /home/user/x-devops/daily-report.sh
```
This runs the full workflow immediately and creates a Gmail draft.

## Next Steps

1. ✅ **Wait for automated run** (9:15 AM tomorrow)
2. ✅ **Check your Gmail drafts folder**
3. ✅ **Review the formatted report**
4. ✅ **Send the draft or customize as needed**

## File Locations

- **Scripts:** `/home/user/x-devops/`
- **Daily Reports:** `/tmp/repo-report-YYYYMMDD.txt`
- **Validation Logs:** `/tmp/repo-validation-YYYYMMDD.log`
- **Latest Report:** `/tmp/latest-repo-report.txt`
- **Documentation:** `/home/user/x-devops/VALIDATION_REPORT_SETUP.md`

---

**Status:** ✅ Active  
**Next Run:** Daily at 9:15 AM  
**Reports:** Auto-generating and sending to Gmail  
**Last Updated:** 2026-07-03
