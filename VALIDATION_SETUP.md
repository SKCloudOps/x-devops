# Daily Repository Validation Setup

This guide helps you set up automated daily repository validation reports sent to your Gmail.

## What's Included

- **Validation Script** (`scripts/daily-repo-validation.sh`) - Analyzes repository for:
  - New commits on the base branch (in last 24 hours)
  - Commits ahead in your current branch
  - Files changed between branches
  - Untracked files
  - Working tree status

- **Task Wrapper** (`scripts/daily-validation-task.sh`) - Orchestrates:
  - Running the validation
  - Sending the report via Gmail
  - Logging results
  - Cleaning up old logs (30-day retention)

- **Report Sender** (`scripts/send-validation-report.sh`) - Handles:
  - Formatting the report
  - Sending via Gmail (multiple methods)
  - Recipient management

## Setup Instructions

### Step 1: Choose Your Email Delivery Method

#### Option A: Gmail SMTP with App Password (Recommended)

1. Enable 2-Step Verification on your Google Account if not already done
2. Generate an App Password:
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will provide a 16-character password
3. Edit `scripts/send-validation-report.sh` and uncomment the SMTP sending section
4. Set environment variable before running:
   ```bash
   export GMAIL_USER="sathishkr.cs@gmail.com"
   export GMAIL_PASSWORD="your-16-char-app-password"
   ```

#### Option B: Gmail API Service Account

1. Create a service account in Google Cloud Console
2. Download the JSON credentials file
3. Place it at: `~/.config/gmail-api-credentials.json`
4. Modify `scripts/send-validation-report.sh` to use the API
5. Install Gmail API client: `pip install google-auth-oauthlib google-auth-httplib2 google-api-client`

#### Option C: Using Claude Code's Gmail Integration

The MCP Gmail tools are already available. Contact support to enable direct draft creation/sending.

### Step 2: Schedule the Daily Task

#### Option A: Using Systemd Timer (Linux)

```bash
# Copy service files to systemd directory
sudo cp .systemd/daily-repo-validation.service /etc/systemd/system/
sudo cp .systemd/daily-repo-validation.timer /etc/systemd/system/

# Enable and start the timer
sudo systemctl enable daily-repo-validation.timer
sudo systemctl start daily-repo-validation.timer

# Check status
sudo systemctl list-timers daily-repo-validation.timer
```

#### Option B: Using Crontab

```bash
# Add to crontab (run daily at 8 AM UTC)
0 8 * * * /home/user/x-devops/scripts/daily-validation-task.sh >> /home/user/x-devops/.validation-logs/cron.log 2>&1
```

#### Option C: Using Claude Code Loop (Coming Soon)

Set up using the `/loop` skill:
```
/loop 24h bash /home/user/x-devops/scripts/daily-validation-task.sh
```

### Step 3: Verify Setup

Test the complete pipeline:
```bash
bash /home/user/x-devops/scripts/daily-validation-task.sh
```

Check the logs:
```bash
tail -f /home/user/x-devops/.validation-logs/$(date '+%Y-%m-%d').log
```

## Configuration Options

Edit `scripts/daily-validation-task.sh` to customize:

```bash
RECIPIENT="${GMAIL_RECIPIENT:-sathishkr.cs@gmail.com}"  # Change recipient
# Add custom environment variables
# Modify logging paths
# Change log retention (default 30 days)
```

## What the Report Includes

Sample report structure:

```
Repository Validation Report
=====================================
Repository: x-devops
Generated: 2026-06-14 15:03:36 UTC

SUMMARY:
--------
Base Branch (main): N new commits in last 24 hours
Current Branch (feature): M commits ahead of base
Changed Files: X
Untracked Files: Y

LAST 5 COMMITS ON BASE BRANCH:
[commit history]

LAST 5 COMMITS ON CURRENT BRANCH:
[commit history]

STATUS: Working tree is [clean/DIRTY]
```

## Troubleshooting

### Email not sending
- Check that GMAIL_PASSWORD or API credentials are set
- Verify the recipient email address in the script
- Check logs: `tail /home/user/x-devops/.validation-logs/cron.log`

### Script not running on schedule
- Verify cron/systemd timer is enabled: `sudo systemctl status daily-repo-validation.timer`
- Check system logs: `journalctl -u daily-repo-validation.service -n 50`

### Permission denied
- Ensure scripts are executable: `chmod +x scripts/*.sh`
- Check directory permissions: `ls -la /home/user/x-devops/`

## Manual Execution

Run validation anytime without scheduling:
```bash
bash /home/user/x-devops/scripts/daily-repo-validation.sh
```

Send a one-time report:
```bash
bash /home/user/x-devops/scripts/daily-validation-task.sh
```

## Next Steps

1. ✅ Review and customize the validation scripts
2. ⚠️ Set up your email delivery method (SMTP, API, or MCP)
3. ⚠️ Schedule the task using your preferred method
4. ✅ Test with: `bash scripts/daily-validation-task.sh`
5. ⚠️ Verify emails are being delivered

## Support

For issues or customizations:
- Check script comments for configuration options
- Review logs in `.validation-logs/` directory
- Run scripts manually to test each component
