# Daily Repository Validation & Email Reports - Setup Guide

## ✅ What's Already Done

Your repository is **ready for automated daily validation reports**. The following components are in place:

### Scripts
- ✅ `validate_and_report.py` - Validates repository and generates HTML reports
- ✅ `send_gmail_report.py` - Sends validation reports via Gmail SMTP
- ✅ `.env.example` - Configuration template

### GitHub Actions Workflow
- ✅ `.github/workflows/daily-validation-report.yml` - Runs daily at **9 AM UTC**
- ✅ Scheduled via cron: `0 9 * * *` (every day at 9 AM UTC)
- ✅ Can be manually triggered via workflow_dispatch

### Validation Includes
✅ Repository name and current branch  
✅ Uncommitted changes count  
✅ New commits from main branch (last 24 hours)  
✅ Detailed commit list with hash, author, date, and message  
✅ Professional HTML formatted email  

---

## 🚀 Next Steps: Configure GitHub Secrets

To enable automated daily emails, add these secrets to your GitHub repository:

### Step 1: Create Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" (if not already enabled)
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows Computer"
5. Copy the 16-character password (remove spaces)

### Step 2: Add GitHub Secrets

Go to your repository: **Settings → Secrets and variables → Actions**

Click "New repository secret" and add these three:

| Secret Name | Value |
|-------------|-------|
| `GMAIL_SENDER_EMAIL` | your-gmail@gmail.com |
| `GMAIL_APP_PASSWORD` | xxxx xxxx xxxx xxxx (remove spaces) |
| `GMAIL_RECIPIENT_EMAIL` | sathishkr.cs@gmail.com |

### Step 3: Verify Setup

Once secrets are added:

1. Go to **Actions** tab in your repository
2. Select **Daily Repository Validation Report** workflow
3. Click **Run workflow** to test immediately
4. Check your email (sathishkr.cs@gmail.com) for the validation report

---

## 📅 Automation Schedule

- **When**: Daily at **9:00 AM UTC**
- **What it does**:
  - Fetches latest changes from remote
  - Validates repository integrity
  - Checks for uncommitted changes
  - Lists new commits from main branch (last 24 hours)
  - Sends HTML email report

---

## 🧪 Manual Testing (Local)

If you want to test locally before GitHub Actions:

```bash
# 1. Create .env file in repository root
cp .env.example .env

# 2. Edit .env with your Gmail credentials
nano .env

# 3. Install dependencies (if needed)
pip install -r requirements.txt

# 4. Run the validation and email script
python3 send_gmail_report.py
```

---

## 📊 Report Content

Each daily email includes:

```
🔍 Repository Validation Report
Generated: [timestamp]

Repository Info
- Repository: x-devops
- Current Branch: [branch-name]

Repository Status
- Uncommitted Changes: [count]
- Status: [clean/modified]

Changes from Main Branch (Last 24 Hours)
- Total New Commits: [count]
- Detailed table with: Hash | Author | Date | Message
```

---

## 🔐 Security Notes

⚠️ **Important:**
- `.env` file is in `.gitignore` and won't be committed
- GitHub Secrets are encrypted and never exposed in logs
- Gmail app password only works for Gmail, not other Google services
- You can revoke app passwords anytime in your Google account settings

---

## 🔧 Customization

You can modify these settings in `.github/workflows/daily-validation-report.yml`:

```yaml
# Change run time (current: 9 AM UTC)
- cron: '0 9 * * *'

# Examples:
# '0 14 * * *'  = 2 PM UTC (9 AM CST)
# '0 0 * * *'   = 12 AM UTC (midnight)
# '30 8 * * *'  = 8:30 AM UTC
```

---

## 📝 Environment Variables Used

The scripts use these environment variables:

```
GMAIL_SENDER_EMAIL     - Your Gmail address (must match app password account)
GMAIL_APP_PASSWORD     - Gmail app-specific password (16 chars, spaces removed)
GMAIL_RECIPIENT_EMAIL  - Where to send reports (can be different email)
```

---

## ✅ Verification Checklist

- [ ] 2-factor authentication enabled on Google account
- [ ] App password created from https://myaccount.google.com/apppasswords
- [ ] GitHub secrets added: GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD, GMAIL_RECIPIENT_EMAIL
- [ ] Workflow manually triggered to test
- [ ] Email received at sathishkr.cs@gmail.com
- [ ] Scheduled daily reports now active

---

## 🆘 Troubleshooting

### Email fails to send
- Verify app password is correct (no spaces)
- Ensure 2-factor authentication is enabled
- Check that GMAIL_SENDER_EMAIL matches your app password account
- Try logging into Gmail to verify account is active

### Workflow not running
- Check Actions tab: Settings → Secrets and variables → Actions
- Ensure all three secrets are added
- Click "Run workflow" to trigger manually for testing

### Git fetch fails
- Verify remote: `git remote -v`
- Check network connectivity
- Ensure repository URL is correct

---

## 📞 Next Steps

1. **Add GitHub Secrets** (as described above)
2. **Test the workflow** (manual trigger from Actions tab)
3. **Verify email delivery** (check your inbox)
4. **Enjoy automated daily reports!** ✅

The automation will now run daily at 9 AM UTC automatically.

---

**Setup completed on**: 2026-07-11  
**Validation tested**: ✅ Working  
**Email configuration**: Pending GitHub Secrets
