# 🚀 Quick Start: Daily Repository Reports

Get your daily repo reports in 5 minutes!

## 1️⃣ Run Interactive Setup

```bash
bash setup_reports.sh
```

This script will:
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Create and configure .env file
- ✅ Test Gmail connection
- ✅ Schedule daily cron job
- ✅ Verify everything works

## 2️⃣ What You'll Need

**One Gmail credential set:**
- Gmail address (e.g., `your-email@gmail.com`)
- 16-character app password from https://myaccount.google.com/apppasswords

**That's it!** The setup script handles the rest.

## 3️⃣ Verify It Works

```bash
# Run a test report immediately
python3 daily_repo_report.py

# Check the logs
tail -f logs/daily_report.log
```

You should receive an email within seconds!

## 4️⃣ Check Your Schedule

```bash
# View your scheduled cron jobs
crontab -l
```

Look for an entry with `daily_repo_report.py`

## 📧 What You'll Receive

Each day you get an email with:
- **Repository status** (clean/with changes)
- **New commits** from the main branch
- **Authors and timestamps**
- **Commit messages**
- **File change statistics**

Example:
```
🔍 Daily Repo Report - x-devops (2026-05-04)

📁 Repository Information
   Repository: x-devops
   Current Branch: main
   Remote URL: http://local_proxy@127.0.0.1:33331/git/SKCloudOps/x-devops
   Local Path: /home/user/x-devops

✅ Repository Status
   Working Directory Status: Clean
   Uncommitted Changes: 0

📝 Main Branch Changes (Last 24 Hours)
   Total new commits: 3

   449c1f5 - Daily tweet by User
   77c0093 - Daily tweet by User
   45ea856 - Daily AI concept by User
```

## 🔧 Manual Run Anytime

```bash
python3 daily_repo_report.py
```

Reports are saved locally to: `reports/`

## ⚙️ Change Your Schedule

Edit your crontab:
```bash
crontab -e
```

Common schedules:
```bash
0 9 * * *     # Daily at 9 AM
0 18 * * *    # Daily at 6 PM
0 */6 * * *   # Every 6 hours
0 8 * * 1-5   # Weekdays at 8 AM
```

## 🐛 Troubleshooting

**Email not sending?**
```bash
# Check credentials
cat .env

# Test directly
python3 daily_repo_report.py
```

**Cron not running?**
```bash
# Check if cron service is active
sudo systemctl status cron

# View recent cron executions
grep CRON /var/log/syslog | tail -10
```

**Missing reports?**
```bash
# Check logs
tail -50 logs/daily_report.log

# Run manually to see any errors
python3 daily_repo_report.py
```

## 📚 Full Documentation

See `SETUP_DAILY_REPORTS.md` for detailed setup and troubleshooting.

## 🎯 Pro Tips

1. **Monitor multiple repos:**
   - Run setup in each repository directory
   - Each will have its own cron job and logs

2. **Change recipient email:**
   - Edit `.env` file
   - Update `GMAIL_RECIPIENT_EMAIL`

3. **Different schedules:**
   - Add multiple cron entries with different commands
   - Each can point to different repos

4. **Share reports:**
   - Set `GMAIL_RECIPIENT_EMAIL` to team email
   - Schedule before team standup time

5. **Archive reports:**
   - Reports are saved in `reports/` directory
   - Can review anytime from email or local files

## ✅ Success Checklist

- [ ] Run `bash setup_reports.sh`
- [ ] Receive first test email
- [ ] See cron job in `crontab -l`
- [ ] Receive daily reports automatically

That's it! You're all set! 🎉
