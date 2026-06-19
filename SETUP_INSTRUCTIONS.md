# Daily Repository Validation Reports - Complete Setup Guide

## 📋 Current Status

**Repository:** x-devops  
**User Email:** sathishkr.cs@gmail.com  
**Setup Date:** 2026-06-19  
**Status:** ⏳ Pending Gmail Configuration  

### ✅ What's Ready
- Repository validation scripts installed
- HTML email template configured
- Python scripts ready to run
- Cron automation option available
- `.env` template created

### ⏳ What's Needed
Your Gmail **app password** to enable automatic email sending

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Your Gmail App Password (2 minutes)

**Why?** Gmail no longer allows regular passwords for apps. You need a special 16-character app password.

1. Go to: **https://myaccount.google.com/security**
2. Turn on **2-Step Verification** (if not already enabled)
3. Go to: **https://myaccount.google.com/apppasswords**
4. Select **Mail** → **Windows Computer**
5. Copy the **16-character password** (you can remove the spaces)

Example: `abcd efgh ijkl mnop` → copy as `abcdefghijklmnop`

### Step 2: Add Your Password to `.env`

Edit the `.env` file in this directory:

```bash
nano /home/user/x-devops/.env
```

Find this line:
```
GMAIL_APP_PASSWORD=
```

Add your 16-character password:
```
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

Save and exit (Ctrl+X, Y, Enter)

### Step 3: Test the Setup

Run this command to send your first test report:

```bash
python3 /home/user/x-devops/send_gmail_report.py
```

You should see:
```
✅ Email sent successfully to sathishkr.cs@gmail.com
```

Check your Gmail inbox for the report!

---

## 📅 Set Up Automatic Daily Reports

Choose ONE of the options below:

### Option A: Linux/Mac Cron Job (Recommended)

Schedule automatic reports for 9 AM every day:

```bash
crontab -e
```

Add this line:
```
0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> /home/user/x-devops/report_logs.txt 2>&1
```

Save (Ctrl+X, Y, Enter)

**View logs:**
```bash
tail -f /home/user/x-devops/report_logs.txt
```

### Option B: Use the Setup Script

```bash
bash /home/user/x-devops/setup_daily_reports.sh
```

This will:
- ✓ Verify your .env configuration
- ✓ Check Python dependencies
- ✓ Test email sending
- ✓ Set up the cron job automatically

### Option C: GitHub Actions

If your repository uses GitHub, create a workflow:

1. Create file: `.github/workflows/daily-report.yml`
2. Copy the content from `AUTOMATED_REPORTS_SETUP.md` (Option 3)
3. Add secrets to your GitHub repository
4. Push the workflow file

---

## 📊 What You'll Get

Each day, you'll receive an email like this:

**Subject:** `Daily Repo Report - x-devops (2026-06-19)`

**Email Contents:**
```
🔍 Repository Validation Report
Generated: 2026-06-19T09:00:00

📌 Repository Info
   Repository: x-devops
   Current Branch: claude/gifted-ride-joeb2i

📊 Repository Status
   Uncommitted Changes: 0
   Status: Clean working directory

📈 Changes from Main Branch (Last 24 Hours)
   Total New Commits: 3

   [Detailed table showing:]
   Hash    | Author      | Date       | Message
   a1b2c3d | John Doe    | 2026-06-19 | Fix bug in validation
   d4e5f6g | Jane Smith  | 2026-06-19 | Update dependencies
   g7h8i9j | Bot         | 2026-06-19 | Merge pull request #42
```

---

## 🧪 Test Without Email

If you just want to test the validation without sending an email:

```bash
python3 /home/user/x-devops/validate_and_report.py
```

This will create an HTML report file showing the validation results.

---

## ❓ Frequently Asked Questions

### Q: Where do I find the Gmail app password?
**A:** https://myaccount.google.com/apppasswords (requires 2-factor authentication)

### Q: Can I use my regular Gmail password?
**A:** No, Gmail blocks regular passwords for apps. You MUST use an app-specific password.

### Q: What if the email goes to spam?
**A:** 
1. Check your Spam folder
2. Mark it as "Not Spam"
3. Gmail will learn and deliver future emails to inbox

### Q: Can I change the report time?
**A:** 
- **Cron:** Change `0 9` to your desired time (e.g., `0 17` for 5 PM)
- **GitHub Actions:** Change `'0 9 * * *'` in the workflow

### Q: Can I see logs of sent reports?
**A:** Yes, check: `/home/user/x-devops/report_logs.txt`

### Q: How do I stop the automatic reports?
**A:** 
```bash
crontab -e
# Delete the line with send_gmail_report.py
```

### Q: What if I lose my app password?
**A:** Go to https://myaccount.google.com/apppasswords and generate a new one, then update .env

---

## 🔒 Security Notes

✅ **DO:**
- Keep your app password safe
- Use app password, not your regular password
- Enable 2-factor authentication
- Keep .env file out of git (it's in .gitignore)

❌ **DON'T:**
- Share your app password
- Commit .env file to git
- Use it for anything other than Gmail
- Store it in plain text elsewhere

---

## 📞 Troubleshooting

### Problem: "Email authentication failed"
**Solution:**
1. Verify GMAIL_SENDER_EMAIL is correct
2. Verify GMAIL_APP_PASSWORD is your 16-char app password (not regular password)
3. Verify 2-factor authentication is enabled
4. Check that the app password hasn't been revoked

### Problem: ".env file not found"
**Solution:**
```bash
# Create it from template
cp /home/user/x-devops/.env.example /home/user/x-devops/.env
# Then edit it with your credentials
nano /home/user/x-devops/.env
```

### Problem: "ModuleNotFoundError: No module named 'dotenv'"
**Solution:**
```bash
pip install -r /home/user/x-devops/requirements.txt
```

### Problem: Script runs but doesn't send email
**Check:** 
1. Are credentials in .env file?
2. Run in verbose mode: `python3 send_gmail_report.py`
3. Check `/home/user/x-devops/report_logs.txt` for errors

---

## ✅ Checklist

Use this checklist to track your setup:

- [ ] Visited https://myaccount.google.com/security and enabled 2-factor authentication
- [ ] Visited https://myaccount.google.com/apppasswords and generated app password
- [ ] Edited `/home/user/x-devops/.env` with app password
- [ ] Tested with: `python3 send_gmail_report.py`
- [ ] Received test email in Gmail inbox
- [ ] Set up automation (cron, GitHub Actions, or other)
- [ ] Verified logs appear in `/home/user/x-devops/report_logs.txt`

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `send_gmail_report.py` | Main script - validates & sends email |
| `validate_and_report.py` | Validates repo & creates HTML report |
| `.env` | Your credentials (NOT in git) |
| `.env.example` | Template for .env |
| `requirements.txt` | Python dependencies |
| `setup_daily_reports.sh` | Automated setup script |
| `AUTOMATED_REPORTS_SETUP.md` | Detailed technical guide |
| `DAILY_REPORTS_SETUP.md` | Original setup documentation |

---

## 🎯 Next Steps

1. **Get your app password** from: https://myaccount.google.com/apppasswords
2. **Edit .env** and add your password
3. **Test:** `python3 send_gmail_report.py`
4. **Automate:** Use cron, GitHub Actions, or the setup script
5. **Enjoy:** Get daily reports in your inbox!

---

Need help? Check the full documentation in `AUTOMATED_REPORTS_SETUP.md`
