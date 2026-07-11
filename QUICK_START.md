# Quick Start: Daily Validation Reports

## ⚡ 3-Minute Setup

### What's happening
Your repository will automatically validate and email daily summaries of:
- Repository status
- New commits from main branch
- Any uncommitted changes

### What you need to do
**Add 3 GitHub Secrets** (5 minutes):

1. Create Gmail app password:
   - Go to https://myaccount.google.com/apppasswords
   - Copy the 16-character password

2. Add to GitHub repository **Settings → Secrets and variables → Actions**:
   ```
   GMAIL_SENDER_EMAIL = your-gmail@gmail.com
   GMAIL_APP_PASSWORD = xxxx xxxx xxxx xxxx
   GMAIL_RECIPIENT_EMAIL = sathishkr.cs@gmail.com
   ```

3. Test it:
   - Go to **Actions** tab
   - Click **Daily Repository Validation Report**
   - Click **Run workflow**
   - Check your email in 30 seconds

### That's it! 🎉

Daily emails will start arriving at **9 AM UTC** automatically.

---

## Current Status

✅ **Validation script**: Working  
✅ **GitHub Actions workflow**: Configured for daily 9 AM UTC  
✅ **Email script**: Ready to send  
⏳ **GitHub Secrets**: Need to be added  
⏳ **First email**: Pending secret configuration  

---

## Files Involved

| File | Purpose |
|------|---------|
| `validate_and_report.py` | Checks repo and generates report |
| `send_gmail_report.py` | Sends report via Gmail |
| `.github/workflows/daily-validation-report.yml` | Schedules daily runs |
| `.env.example` | Config template (for local testing) |

---

## FAQ

**Q: When does it run?**  
A: Daily at 9 AM UTC. Change it in `.github/workflows/daily-validation-report.yml`

**Q: Can I test it now?**  
A: Yes! Manually trigger from Actions tab after adding secrets.

**Q: What if I don't want daily emails?**  
A: Disable the workflow or delete the `.github/workflows/daily-validation-report.yml` file.

**Q: Can I change the recipient email?**  
A: Yes, update `GMAIL_RECIPIENT_EMAIL` secret in GitHub.

**Q: Is my Gmail password safe?**  
A: Yes! GitHub encrypts secrets. Plus you're using an app-specific password (not your real password).

---

## Need Help?

See `SETUP_COMPLETE.md` for detailed troubleshooting and customization options.
