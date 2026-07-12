# ⚡ Quick Start - Daily Reports (3 Steps)

## Your Setup Status
✅ Repository validation infrastructure ready  
✅ Gmail sending capability configured  
✅ GitHub Actions workflow in place  
⏳ **NEXT: Add Gmail credentials**

---

## 3-Step Setup

### 1️⃣ Enable Gmail Authentication

**Go to:** https://myaccount.google.com/security
- Enable "2-Step Verification" (if not already enabled)

**Go to:** https://myaccount.google.com/apppasswords
- Select: "Mail" + "Windows Computer"
- Click: "Generate"
- **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

### 2️⃣ Create Configuration File

**Create file:** `/home/user/x-devops/.env`

**Add this content:**
```
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
```

**Replace:**
- `your-email@gmail.com` → Your actual Gmail
- `xxxx xxxx xxxx xxxx` → Your 16-char password from step 1
- Keep recipient as is

### 3️⃣ Test It Works

```bash
python3 send_gmail_report.py
```

**Expected:** Email sent to sathishkr.cs@gmail.com ✅

---

## Automate

### Option A: GitHub Actions (Recommended)

1. Go to GitHub → Settings → Secrets and variables → Actions
2. Add three secrets (same values as .env):
   - `GMAIL_SENDER_EMAIL`
   - `GMAIL_APP_PASSWORD`
   - `GMAIL_RECIPIENT_EMAIL`

3. **Done!** Workflow runs daily at 9 AM UTC

### Option B: Cron Job (Local)

```bash
crontab -e
```

Add line:
```
0 9 * * * cd /home/user/x-devops && python3 send_gmail_report.py >> report_logs.txt 2>&1
```

Save and exit. **Done!**

---

## Verify Setup

```bash
python3 verify_setup.py
```

All checks should show ✓

---

## Daily Report Includes

📋 Repository name & branch  
🔍 Uncommitted changes count  
📈 New commits (last 24 hours)  
📊 Detailed commit info (hash, author, date, message)  

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Email fails | ✓ Enable 2FA on Google account |
| | ✓ Check app password is correct |
| | ✓ Verify .env file exists & has values |
| .env not found | ✓ Create at `/home/user/x-devops/.env` |
| Cron not running | ✓ Check with: `crontab -l` |
| | ✓ Test manually: `python3 send_gmail_report.py` |

---

## Files for Reference

- **IMPLEMENTATION_SUMMARY.md** - Full overview
- **SETUP_GUIDE.md** - Detailed instructions
- **verify_setup.py** - Check your configuration

---

## That's It! 🎉

You're ~5 minutes away from daily automated validation reports in your inbox!

**Next:** Create `.env` file → Run test → Enable automation
