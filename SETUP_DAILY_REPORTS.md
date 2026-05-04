# Daily Repository Validation & Reporting Setup

This guide will help you set up automated daily repository validation reports sent to your Gmail inbox.

## Quick Setup (5 minutes)

### Step 1: Create .env File

Copy the example configuration:
```bash
cp .env.example .env
```

### Step 2: Configure Gmail Credentials

You need to:
1. **Enable 2-Factor Authentication** on your Google Account
2. **Generate an App Password** at https://myaccount.google.com/apppasswords
3. **Update your .env file**

#### Detailed Steps:

#### A. Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Look for "2-Step Verification" and enable it
3. Follow the Google setup wizard

#### B. Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select: **Mail** and **Windows Computer**
3. Click **Generate**
4. Gmail will show you a 16-character password (with spaces like: `xxxx xxxx xxxx xxxx`)
5. Copy this password

#### C. Update .env File
Edit `.env` with:
```
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_RECIPIENT_EMAIL=your-email@gmail.com
```

**Note:** 
- GMAIL_SENDER_EMAIL must be your full Gmail address
- GMAIL_APP_PASSWORD is the 16-character code from step B (spaces are OK, they're automatically removed)
- GMAIL_RECIPIENT_EMAIL can be any email address that should receive the reports

### Step 3: Test the Setup

Run the report generator manually:
```bash
python3 daily_repo_report.py
```

You should see:
- ✅ Validation checks
- 📧 Email successfully sent to your recipient
- 💾 Report saved locally to `reports/` directory

## Automated Daily Execution

### Option A: Using Cron (Linux/Mac)

1. **Open your crontab:**
```bash
crontab -e
```

2. **Add one of these lines** (pick a time that works for you):

**Daily at 9:00 AM:**
```
0 9 * * * cd /home/user/x-devops && /usr/bin/python3 daily_repo_report.py >> /home/user/x-devops/logs/daily_report.log 2>&1
```

**Daily at 6:00 PM:**
```
0 18 * * * cd /home/user/x-devops && /usr/bin/python3 daily_repo_report.py >> /home/user/x-devops/logs/daily_report.log 2>&1
```

**Every 6 hours:**
```
0 */6 * * * cd /home/user/x-devops && /usr/bin/python3 daily_repo_report.py >> /home/user/x-devops/logs/daily_report.log 2>&1
```

**Every business day at 8:00 AM (Mon-Fri):**
```
0 8 * * 1-5 cd /home/user/x-devops && /usr/bin/python3 daily_repo_report.py >> /home/user/x-devops/logs/daily_report.log 2>&1
```

3. **Create logs directory:**
```bash
mkdir -p /home/user/x-devops/logs
```

4. **Save and exit** (in nano: `Ctrl+X`, then `Y`, then `Enter`)

### Option B: Using a Shell Script

Create a wrapper script for easier scheduling:

```bash
#!/bin/bash
# save as: run_daily_report.sh

set -e

REPO_DIR="/home/user/x-devops"
SCRIPT="$REPO_DIR/daily_repo_report.py"
LOG_DIR="$REPO_DIR/logs"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/daily_report_$(date +%Y%m%d_%H%M%S).log"

cd "$REPO_DIR"

echo "=== Daily Repository Report ===" >> "$LOG_FILE"
echo "Started at $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

if python3 "$SCRIPT" >> "$LOG_FILE" 2>&1; then
    echo "" >> "$LOG_FILE"
    echo "✅ Report completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "" >> "$LOG_FILE"
    echo "❌ Report failed at $(date)" >> "$LOG_FILE"
    exit 1
fi
```

Make it executable:
```bash
chmod +x /home/user/x-devops/run_daily_report.sh
```

Then add to crontab:
```
0 9 * * * /home/user/x-devops/run_daily_report.sh
```

### Option C: Using Systemd Timer (Advanced - Linux Only)

Create `/etc/systemd/system/daily-repo-report.service`:
```ini
[Unit]
Description=Daily Repository Validation Report
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/home/user/x-devops
ExecStart=/usr/bin/python3 daily_repo_report.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/daily-repo-report.timer`:
```ini
[Unit]
Description=Run Daily Repository Report
Requires=daily-repo-report.service

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable daily-repo-report.timer
sudo systemctl start daily-repo-report.timer
```

Check status:
```bash
sudo systemctl status daily-repo-report.timer
sudo systemctl list-timers daily-repo-report.timer
```

## Verification

### Check if cron job is running:
```bash
# List your cron jobs
crontab -l

# Check cron logs (Linux)
grep CRON /var/log/syslog | tail -20

# Check logs from the script
tail -f /home/user/x-devops/logs/daily_report.log
```

### Test the setup:
```bash
# Run manually to verify everything works
python3 daily_repo_report.py

# Check the generated reports
ls -lh /home/user/x-devops/reports/
```

## Troubleshooting

### Email Not Sending

**Problem:** "Gmail authentication failed"

**Solutions:**
1. Verify 2-Factor Authentication is enabled
2. Generate a new App Password at https://myaccount.google.com/apppasswords
3. Copy it exactly (spaces don't matter but must match)
4. Test: `python3 daily_repo_report.py`

### Cron Job Not Running

1. **Check if cron is running:**
   ```bash
   sudo systemctl status cron
   ```

2. **Verify Python path:**
   ```bash
   which python3
   ```
   Use the full path (e.g., `/usr/bin/python3`)

3. **Check permissions:**
   ```bash
   chmod +x /home/user/x-devops/daily_repo_report.py
   ```

4. **Test cron environment:**
   ```bash
   # Create test cron job that just writes to a file
   (crontab -l; echo "* * * * * /bin/echo 'test' >> /tmp/cron_test.txt") | crontab -
   # Wait a minute, then check
   cat /tmp/cron_test.txt
   ```

### Missing .env Variables

**Problem:** "Gmail credentials not configured!"

**Solution:**
```bash
# Verify .env file exists and has content
cat /home/user/x-devops/.env

# Should output:
# GMAIL_SENDER_EMAIL=your-email@gmail.com
# GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
# GMAIL_RECIPIENT_EMAIL=recipient@example.com
```

### Permission Denied When Opening .env

```bash
chmod 600 /home/user/x-devops/.env
```

## What the Report Includes

Each daily email report contains:

- **Repository Information**: Name, remote URL, current branch, local path
- **Repository Status**: Working directory state, uncommitted changes
- **Main Branch Changes**: All commits from the last 24 hours with:
  - Commit hash
  - Author name
  - Commit date
  - Commit message
- **File Changes**: Statistics on which files were modified
- **Generated**: Timestamp of report generation

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GMAIL_SENDER_EMAIL` | Yes | Your Gmail address | `user@gmail.com` |
| `GMAIL_APP_PASSWORD` | Yes | 16-char app password | `xxxx xxxx xxxx xxxx` |
| `GMAIL_RECIPIENT_EMAIL` | No | Report recipient | `reports@example.com` |

## Support

For issues or questions:
1. Check the logs in `/home/user/x-devops/logs/`
2. Run the script manually: `python3 daily_repo_report.py`
3. Verify .env file permissions: `ls -la .env`
4. Test Gmail credentials independently

## Security Notes

- ✅ .env is in .gitignore (won't be committed)
- ✅ App passwords are safer than regular passwords
- ✅ Run with appropriate file permissions (600)
- ✅ Logs don't contain sensitive credentials
- Always keep your app password safe and regenerate if compromised

## Next Steps

1. ✅ Copy .env.example to .env
2. ✅ Generate Gmail app password
3. ✅ Update .env with credentials
4. ✅ Test: `python3 daily_repo_report.py`
5. ✅ Set up cron job for daily execution
6. ✅ Verify logs to confirm it's working

Happy reporting! 📊
