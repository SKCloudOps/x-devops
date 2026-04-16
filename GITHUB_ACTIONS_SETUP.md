# GitHub Actions Setup for Daily Validation Reports

This guide helps you set up GitHub Actions to automatically run daily validation reports.

## What's Included

- `.github/workflows/daily-validation-report.yml` - GitHub Actions workflow
- Scheduled to run daily at 9 AM UTC (adjustable)
- Manual trigger option available
- Automatic artifact retention for 7 days

## Setup Instructions

### Step 1: Get Gmail App Password

If you haven't already, follow these steps to generate an app password:

#### 1a. Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Click on "2-Step Verification"
3. Follow the prompts to enable it

#### 1b. Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" from the app dropdown
3. Select "Windows Computer" from the device dropdown
4. Click "Generate"
5. Google will display a 16-character password (with spaces)
6. **Copy this password** - you'll need it for the next step

**Example:** `abcd efgh ijkl mnop`

### Step 2: Add GitHub Secrets

1. Go to your GitHub repository: https://github.com/SKCloudOps/x-devops

2. Click on **Settings** → **Secrets and variables** → **Actions**

3. Click **"New repository secret"** and add these three secrets:

#### Secret 1: GMAIL_SENDER_EMAIL
- **Name:** `GMAIL_SENDER_EMAIL`
- **Value:** Your Gmail address (e.g., `your-email@gmail.com`)

#### Secret 2: GMAIL_APP_PASSWORD
- **Name:** `GMAIL_APP_PASSWORD`
- **Value:** The 16-character password you copied above (you can remove spaces or keep them)

#### Secret 3: GMAIL_RECIPIENT_EMAIL
- **Name:** `GMAIL_RECIPIENT_EMAIL`
- **Value:** `sathishkrcs@gmail.com` (or another email to receive reports)

### Step 3: Verify the Workflow

1. Go to your repository's **Actions** tab
2. You should see "Daily Repository Validation Report" workflow
3. The workflow will run automatically at 9 AM UTC daily
4. You can manually trigger it by clicking "Run workflow"

## Manual Trigger

To run a report right now:

1. Go to **Actions** tab
2. Select "Daily Repository Validation Report"
3. Click "Run workflow" button
4. Wait for it to complete

## Schedule Customization

To change when the report runs, edit `.github/workflows/daily-validation-report.yml`:

Current schedule:
```yaml
- cron: '0 9 * * *'  # 9 AM UTC daily
```

**Common cron examples:**
- `'0 8 * * *'` - 8 AM UTC daily
- `'0 9 * * 1'` - 9 AM UTC every Monday
- `'0 9 * * 1-5'` - 9 AM UTC weekdays only
- `'0 9 1 * *'` - 9 AM UTC first day of each month

[Cron syntax reference](https://crontab.guru/)

## Monitoring Reports

### View Logs
1. Go to **Actions** tab
2. Click on a workflow run
3. Click on the "validate-and-report" job
4. Scroll down to see the output

### Download Report Data
1. Go to **Actions** tab
2. Click on a completed workflow run
3. Scroll down to "Artifacts" section
4. Download "validation-report-logs" (contains JSON report data)

## Troubleshooting

### Workflow fails to run

**Issue:** "Failed to send email"
- **Solution:** Verify all three secrets are set correctly in Settings → Secrets
- Check that GMAIL_SENDER_EMAIL has 2-factor authentication enabled

**Issue:** "Repository not found"
- **Solution:** Ensure the workflow has proper checkout permissions
- Go to Settings → Actions → General → Workflow permissions → select "Read and write permissions"

**Issue:** "ModuleNotFoundError: No module named 'dotenv'"
- **Solution:** This shouldn't happen as `python-dotenv` is in requirements.txt
- Try re-running the workflow

### No email received

1. Check Gmail spam folder
2. Verify sender email is correct (the one that generated the app password)
3. Check GitHub Actions logs for error messages
4. Verify app password is still valid (not revoked)

## Security Considerations

✅ **Good practices:**
- Secrets are encrypted and never shown in logs
- The `.env` file is in `.gitignore` (local development)
- GitHub Actions uses read-only repository access

⚠️ **Important:**
- Never commit your `.env` file to the repository
- The app password only works for Gmail
- You can revoke the app password anytime in Google Account settings
- Only authorized GitHub Actions runs can access secrets

## Testing

To test the setup without waiting for the scheduled time:

1. Go to **Actions** tab
2. Select "Daily Repository Validation Report"
3. Click "Run workflow"
4. Select the branch (usually "main" or your current branch)
5. Watch the logs in real-time

Expected output in logs:
```
🔍 Starting repository validation and email sending...
📥 Fetching latest changes from remote...
✅ Validating repository...
...
📧 Sending report to sathishkrcs@gmail.com...
✅ Email sent successfully to sathishkrcs@gmail.com
```

## Disabling the Workflow

If you want to temporarily disable the scheduled reports:

1. Go to **Actions** tab
2. Click on "Daily Repository Validation Report"
3. Click the "..." menu → "Disable workflow"
4. To re-enable: Click the same menu → "Enable workflow"

## Additional Notes

- The workflow uses `python-3.10` and `ubuntu-latest` (newest available)
- Reports are generated with full git history (`fetch-depth: 0`)
- Report data artifacts are kept for 7 days (adjustable in the workflow file)
- The workflow logs are kept according to GitHub's retention policy

## Next Steps

1. ✅ Set up the three GitHub Secrets (see Step 2 above)
2. ✅ Trigger the workflow manually to test
3. ✅ Monitor the first scheduled run
4. ✅ Check your Gmail for the report

That's it! Your daily validation reports are now automated! 🎉
