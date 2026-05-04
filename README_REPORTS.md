# 📊 Daily Repository Validation & Email Reports

Automated repository validation with daily email reports to your Gmail inbox.

## Overview

This solution provides:

✅ **Repository Validation**
- Git status checks
- Uncommitted changes detection
- Branch information
- Commit history analysis

✅ **Daily Email Reports**
- Automatic scheduling (via cron)
- Professional HTML emails
- Detailed commit information
- File change statistics

✅ **Easy Setup**
- Interactive setup wizard
- One-command configuration
- Automatic Gmail credential handling
- Built-in testing

## Files Overview

| File | Purpose |
|------|---------|
| `daily_repo_report.py` | Main validation & reporting script |
| `setup_reports.sh` | Interactive setup wizard |
| `run_report.sh` | Manual report runner |
| `QUICK_START.md` | 5-minute quick start guide |
| `SETUP_DAILY_REPORTS.md` | Detailed setup documentation |
| `.env` | Gmail credentials (created during setup) |
| `logs/` | Daily execution logs |
| `reports/` | Local HTML report archives |

## Getting Started

### Step 1: Run Setup (Required)

```bash
bash setup_reports.sh
```

The wizard will guide you through:
1. ✅ Dependency checks
2. ✅ Gmail credential configuration
3. ✅ Test email sending
4. ✅ Cron job scheduling
5. ✅ Verification

### Step 2: Run Manually (Optional)

```bash
bash run_report.sh
```

Or directly:
```bash
python3 daily_repo_report.py
```

### Step 3: Verify Automation (Optional)

```bash
# Check scheduled jobs
crontab -l

# Monitor logs
tail -f logs/daily_report.log
```

## Configuration

### Gmail Setup

1. **Enable 2-Factor Authentication:**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select Mail → Windows Computer
   - Click Generate
   - Copy the 16-character password

3. **Configure .env:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Cron Scheduling

Automatically configured by `setup_reports.sh`, but you can manually edit:

```bash
crontab -e
```

Add any of these:
```bash
0 9 * * *       # Daily at 9:00 AM
0 18 * * *      # Daily at 6:00 PM
0 */6 * * *     # Every 6 hours
0 8 * * 1-5     # Weekdays at 8:00 AM
*/30 * * * *    # Every 30 minutes
```

## Report Contents

Each daily email includes:

- **Repository Information**
  - Repository name
  - Current branch
  - Remote URL
  - Local path

- **Repository Status**
  - Working directory cleanliness
  - Count of uncommitted changes
  - List of modified files

- **Commit History (Last 24 Hours)**
  - Commit hash
  - Author name & email
  - Commit date
  - Commit message

- **File Statistics**
  - Changed files count
  - Insertions/deletions summary

## Examples

### Run Report and Email Immediately

```bash
python3 daily_repo_report.py
```

Output:
```
======================================================================
🚀 Daily Repository Validation and Report Generator
======================================================================
📥 Fetching latest changes from remote...
✅ Fetch successful
✅ Validating repository...

======================================================================
📊 VALIDATION SUMMARY
======================================================================
Repository: x-devops
Current Branch: main
Uncommitted Changes: 0
New Commits on Main (24h): 3
======================================================================

📝 Generating HTML report...
💾 Report saved to: reports/repo_validation_20260504_120000.html

📧 Sending report to recipient@gmail.com...
📧 Connecting to Gmail SMTP server...
   Sender: your-email@gmail.com
   Recipient: recipient@gmail.com
✅ Email sent successfully to recipient@gmail.com

======================================================================
✅ SUCCESS: Repository validation and report complete!
======================================================================
```

### Check Automation Status

```bash
$ crontab -l
0 9 * * * cd /home/user/x-devops && /usr/bin/python3 daily_repo_report.py >> /home/user/x-devops/logs/daily_report.log 2>&1

$ tail logs/daily_report.log
=== Daily Repository Report ===
Started at Sun May  4 09:00:01 UTC 2026
✅ Report completed successfully at Sun May  4 09:00:15 UTC 2026
```

## Troubleshooting

### Common Issues

#### 1. "Gmail authentication failed"

```bash
# Verify credentials
cat .env | grep GMAIL

# Test script
python3 daily_repo_report.py
```

**Solutions:**
- Verify Gmail address is correct
- Generate new app password at https://myaccount.google.com/apppasswords
- Ensure 2FA is enabled

#### 2. "Cron job not running"

```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Verify Python path
which python3
```

#### 3. "Email never arrives"

```bash
# Check logs for errors
tail -100 logs/daily_report.log | grep -i error

# Check Gmail IMAP isn't blocking
# https://myaccount.google.com/lesssecureapps
```

#### 4. "Reports directory not created"

```bash
# Create it manually
mkdir -p reports

# Run script again
python3 daily_repo_report.py
```

## Monitoring

### View Logs

```bash
# Last 10 entries
tail -n 10 logs/daily_report.log

# Last 50 entries with timestamps
tail -n 50 logs/daily_report.log

# Real-time monitoring
tail -f logs/daily_report.log

# Search for errors
grep -i error logs/daily_report.log

# View specific date
grep "2026-05-04" logs/daily_report.log
```

### View Reports

```bash
# List all generated reports
ls -lh reports/

# View latest report in browser
open reports/repo_validation_*.html

# Count daily reports
ls reports/ | wc -l
```

### Cron Status

```bash
# List all cron jobs
crontab -l

# Check if cron service is running
sudo systemctl is-active cron

# View recent cron executions
sudo grep CRON /var/log/syslog | tail -5
```

## Security

✅ **Best Practices:**
- App password stored in .env (git-ignored)
- .env file permissions: 600 (read/write only by owner)
- Never commit .env to repository
- Regenerate app password if compromised
- Cron logs don't contain sensitive data

**File Permissions:**
```bash
# Check .env permissions
ls -la .env

# Set correct permissions if needed
chmod 600 .env
```

## Advanced Usage

### Multiple Repositories

Set up in each repository:
```bash
cd /path/to/repo1
bash setup_reports.sh

cd /path/to/repo2
bash setup_reports.sh
```

Each will have separate cron jobs and logs.

### Custom Email Recipients

Edit `.env` to send to different emails:
```bash
GMAIL_RECIPIENT_EMAIL=team@example.com
```

### Different Schedules

Add multiple cron jobs:
```bash
crontab -e

# First repo at 9 AM
0 9 * * * cd /repo1 && python3 daily_repo_report.py >> logs/report.log 2>&1

# Second repo at 6 PM
0 18 * * * cd /repo2 && python3 daily_repo_report.py >> logs/report.log 2>&1
```

### Integrate with CI/CD

Run as part of your CI/CD pipeline:
```yaml
# Example GitHub Actions
- name: Send Daily Report
  run: python3 daily_repo_report.py
  env:
    GMAIL_SENDER_EMAIL: ${{ secrets.GMAIL_EMAIL }}
    GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_PASSWORD }}
    GMAIL_RECIPIENT_EMAIL: ${{ secrets.REPORT_EMAIL }}
```

## Support & Help

1. **Quick Start:**
   ```bash
   cat QUICK_START.md
   ```

2. **Detailed Setup:**
   ```bash
   cat SETUP_DAILY_REPORTS.md
   ```

3. **Test Script:**
   ```bash
   python3 daily_repo_report.py
   ```

4. **Check Logs:**
   ```bash
   tail -f logs/daily_report.log
   ```

## License

This is part of the x-devops repository.

---

**Ready to get started?** Run `bash setup_reports.sh` and follow the interactive guide!
