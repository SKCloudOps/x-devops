# Setup Daily Repository Validation Reports

This guide will help you set up automated daily validation reports sent to your Gmail inbox.

## What You'll Get

✅ **Daily at 9 AM UTC** (configurable)
- Repository validation status
- New commits on the main branch (last 24 hours)
- Commit details (hash, author, date, message)
- Current branch info and uncommitted changes
- Professional HTML-formatted email

## Quick Setup (5 minutes)

### Step 1: Enable 2-Factor Authentication (if not already done)

1. Go to https://myaccount.google.com/security
2. Find "2-Step Verification" and enable it
3. Follow Google's verification process

### Step 2: Create a Gmail App Password

1. Visit https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Google will generate a **16-character password** (with spaces)
   - Example: `abcd efgh ijkl mnop`
4. **Copy this password** - you'll use it in the next step
5. ⚠️ **Do NOT** use your regular Gmail password

### Step 3: Add GitHub Secrets

1. Go to your GitHub repository: https://github.com/skcloudops/x-devops
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these three secrets:

#### Secret 1: GMAIL_SENDER_EMAIL
- **Name:** `GMAIL_SENDER_EMAIL`
- **Value:** Your Gmail address (e.g., `sathishkr.cs@gmail.com`)

#### Secret 2: GMAIL_APP_PASSWORD
- **Name:** `GMAIL_APP_PASSWORD`
- **Value:** The 16-character password from Step 2
- *Note: You can include or remove spaces, both work*

#### Secret 3: GMAIL_RECIPIENT_EMAIL
- **Name:** `GMAIL_RECIPIENT_EMAIL`
- **Value:** Where to send reports (e.g., `sathishkr.cs@gmail.com`)
- *Tip: Can be same as GMAIL_SENDER_EMAIL, or different email*

### Step 4: Test the Setup

1. In GitHub, go to **Actions** tab
2. Find the workflow: **Daily Repository Validation Report**
3. Click **Run workflow** → **Run workflow** button
4. Wait 1-2 minutes for it to complete
5. Check your Gmail inbox for the test report
6. If successful, daily reports will start automatically

## Troubleshooting

### ❌ "Gmail authentication failed"
- ✅ Verify GMAIL_SENDER_EMAIL is correct
- ✅ Verify GMAIL_APP_PASSWORD is the 16-character app password (not your regular password)
- ✅ Confirm 2-factor authentication is enabled on your Google account
- ✅ Check that the app password hasn't been revoked in Google Account settings
- ✅ Try removing spaces from the app password in the secret

### ❌ "Email fails to send"
- ✅ Verify both email secrets are set correctly
- ✅ Check GitHub Actions logs for detailed error messages
- ✅ Try running the workflow manually again with fresh credentials

### ❌ "Repository validation failed"
- ✅ Ensure `requirements.txt` has all dependencies
- ✅ Check that git remote is accessible
- ✅ Verify branch names in the validation script

## Customization

### Change Report Time

Edit `.github/workflows/daily-validation-report.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change "9" to your preferred hour (UTC)
```

**Cron format:** `minute hour day month day-of-week`
- `0 8 * * *` = 8 AM UTC daily
- `0 18 * * *` = 6 PM UTC daily
- `0 10 * * 1-5` = 10 AM UTC weekdays only

### Change Report Content

Edit `send_gmail_report.py` to:
- Adjust the `days` parameter in `get_git_log()` (default: 1 day)
- Modify the HTML report formatting in `format_html_report()`
- Add more branches to the report
- Include additional validation checks

### Multiple Recipients

Modify `send_gmail_report.py`:

```python
recipient_email = os.getenv('GMAIL_RECIPIENT_EMAIL', 'sathishkr.cs@gmail.com').strip()
# Split by comma for multiple recipients
recipients = [r.strip() for r in recipient_email.split(',')]
for recipient in recipients:
    success = send_via_gmail(recipient, subject, html_report, sender_email, app_password)
```

## Security Notes

⚠️ **Important:**
- The `.env` file is in `.gitignore` - it's never committed to the repository
- GitHub Secrets are encrypted and only accessible during workflow runs
- The app password only works for Gmail, not other Google services
- You can revoke the app password anytime at: https://myaccount.google.com/apppasswords

## How It Works

1. **GitHub Actions** runs the workflow on schedule (default: 9 AM UTC daily)
2. **Python script** (`send_gmail_report.py`):
   - Fetches latest changes from git
   - Validates repository status
   - Generates HTML-formatted report
   - Sends via Gmail SMTP
3. **Email arrives** in your inbox with:
   - Current branch info
   - Uncommitted changes status
   - New commits from main branch (last 24h)
   - Detailed commit list with author/date/message

## Manual Testing

To test locally before setting up GitHub secrets:

1. Create a `.env` file in the repository root:
   ```
   GMAIL_SENDER_EMAIL=your-email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   GMAIL_RECIPIENT_EMAIL=sathishkr.cs@gmail.com
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:
   ```bash
   python3 send_gmail_report.py
   ```

4. Check your inbox for the test email

## Next Steps

- ✅ Complete the setup steps above
- ✅ Test by running the workflow manually
- ✅ Adjust the schedule time if needed
- ✅ Start receiving daily validation reports!

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GitHub Actions logs for detailed error messages
3. Verify all secrets are set correctly in GitHub Settings
4. Check that Gmail app password is valid and not revoked

---

**Questions?** The setup is designed to be simple and secure. All credentials are encrypted by GitHub and never exposed in logs.
