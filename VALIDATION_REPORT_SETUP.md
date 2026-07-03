# Daily Repository Validation & Gmail Reporting Setup

## Overview
This automation system validates your `x-devops` repository daily and sends comprehensive reports to your Gmail inbox. The system checks for new commits, changes, and repository health.

## Components

### 1. **daily-validation.sh** (Core Validation Script)
Performs repository validation and generates detailed reports.

**What it checks:**
- Repository accessibility and remote configuration
- Current branch status and comparison with base branch (main)
- New commits from base branch (last 24 hours)
- Uncommitted changes
- Commit history
- Branch status

**Output:**
- Logs validation steps to `/tmp/repo-validation-YYYYMMDD.log`
- Generates report at `/tmp/repo-report-YYYYMMDD.txt`
- Stores latest report at `/tmp/latest-repo-report.txt` for email sending

### 2. **daily-report.sh** (Master Orchestration Script)
Coordinates the entire validation and reporting workflow.

**Steps:**
1. Runs repository validation
2. Verifies report generation
3. Creates Gmail draft with formatted report
4. Provides colored console output for easy monitoring

**Run manually:**
```bash
bash /home/user/x-devops/daily-report.sh
```

### 3. **send-report.py** (Helper Script)
Python script for processing and preparing reports for email delivery.

## Scheduled Automation

### Daily Schedule
- **Frequency:** Every day at 9:15 AM
- **Timezone:** Your local timezone
- **Duration:** ~30-60 seconds per run
- **Auto-expiry:** Jobs auto-expire after 7 days (session-only)

### Cron Job Details
```
Job ID: 05df8e07
Cron Expression: 15 9 * * *
Status: Active
Recurrence: Daily
```

## Gmail Integration

### Current Setup
- **Recipient Email:** sathishkr.cs@gmail.com
- **Report Type:** HTML formatted with styling
- **Delivery Method:** Gmail Draft (auto-created, ready to review)

### Gmail Features
- ✓ Formatted HTML reports with colors and tables
- ✓ Branch comparison statistics
- ✓ Commit history table
- ✓ Validation check results
- ✓ Summary statistics

### How Reports Are Delivered
1. **Automated Draft Creation:** System creates a Gmail draft at 9:15 AM
2. **Manual Review:** Check your Gmail drafts folder
3. **Send Option:** You can review and send the draft, or it can be sent automatically in future iterations

### Report Contents
Each report includes:
- Repository status (current branch, base branch, uncommitted changes)
- Branch comparison (commits ahead, new commits in base)
- Latest commits table with commit hash and message
- Validation checks (accessibility, remote configuration, commit status)
- Uncommitted files list
- Overall health summary

## Validation Report Example

```
================================================================================
DAILY REPOSITORY VALIDATION REPORT - x-devops
Generated: 2026-07-03 15:09:36
================================================================================

REPOSITORY STATUS:
  Current Branch: claude/gifted-ride-4r1o75
  Base Branch: main
  Uncommitted Changes: 2
  
BRANCH COMPARISON:
  Commits ahead of main: 0
  New commits in main (last 24h): 0

GIT VALIDATION CHECKS:
  ✓ Repository is accessible
  ✓ Remote is configured
  ✗ No new commits in base branch (last 24h)
  ✗ Uncommitted changes present
```

## Manual Testing

### Test the complete workflow:
```bash
bash /home/user/x-devops/daily-report.sh
```

### Test validation only:
```bash
bash /home/user/x-devops/daily-validation.sh
```

### Check latest report:
```bash
cat /tmp/latest-repo-report.txt
```

### View logs:
```bash
cat /tmp/repo-validation-$(date +%Y%m%d).log
```

## Troubleshooting

### Issue: Scripts not found
**Solution:** Ensure scripts are in `/home/user/x-devops/` and are executable:
```bash
chmod +x /home/user/x-devops/*.sh
```

### Issue: Git operations failing
**Solution:** Verify git configuration:
```bash
cd /home/user/x-devops
git status
git remote -v
```

### Issue: Gmail drafts not appearing
**Solution:** Check Gmail inbox and drafts folder. Verify email address in configuration.

### Issue: Reports not generating
**Solution:** Check log files:
```bash
tail -f /tmp/repo-validation-*.log
```

## Configuration

### To modify recipient email:
Edit the email address in `/home/user/x-devops/daily-validation.sh`:
```bash
RECIPIENT_EMAIL="your-email@gmail.com"
```

### To change schedule time:
The current schedule is 9:15 AM daily. To modify:
- Delete current job: `CronDelete 05df8e07`
- Create new job with different time (e.g., 3 PM = `15 3 * * *`)

### To adjust validation checks:
Edit `/home/user/x-devops/daily-validation.sh` and modify the git commands or checks.

## Files Structure

```
/home/user/x-devops/
├── daily-validation.sh          # Core validation script
├── daily-report.sh              # Master orchestration script
├── send-report.py               # Helper script
├── VALIDATION_REPORT_SETUP.md   # This file
└── /tmp/
    ├── repo-validation-*.log    # Validation logs
    ├── repo-report-*.txt        # Daily reports
    └── latest-repo-report.txt   # Latest report for email
```

## Future Enhancements

Possible improvements for future iterations:
- [ ] Direct email sending (auto-send instead of draft-only)
- [ ] Slack integration for notifications
- [ ] GitHub PR comments with validation results
- [ ] Email attachments with detailed logs
- [ ] Custom validation rules and checks
- [ ] Multiple repository support
- [ ] Trend tracking and historical comparison

## Support & Monitoring

### Check automation status:
```bash
# View active cron jobs
# Job should fire automatically at 9:15 AM daily
```

### Review created drafts:
- Go to Gmail → Drafts
- Look for emails titled "Daily Repository Validation Report - x-devops"

### Check recent validations:
```bash
ls -lt /tmp/repo-report-*.txt | head -5
```

## Summary

✅ **Setup Complete!**
- Daily validation: Configured
- Scheduled automation: Active (9:15 AM)
- Gmail integration: Ready
- Reports: Auto-generating and creating drafts

**Next Steps:**
1. Wait for the first automated run (9:15 AM tomorrow)
2. Check your Gmail drafts for the report
3. Review the report format and adjust as needed
4. Customize email recipients or schedule as required

---

**Created:** 2026-07-03
**Status:** Active
**Job ID:** 05df8e07
