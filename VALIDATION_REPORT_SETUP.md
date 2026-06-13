# Daily Repository Validation & Email Report Setup

This guide helps you set up automated daily repository validation reports that are sent to your Gmail inbox.

## Overview

The system consists of three main components:

1. **Validation Script** (`scripts/validate_and_report.sh`) - Validates the repository and generates a detailed report
2. **Email Generator** (`scripts/send_daily_report.py`) - Prepares the validation report for sending via Gmail
3. **Scheduler** - Runs the scripts on a daily schedule (GitHub Actions or Cron)

## Features

- ✅ Repository status validation
- ✅ New commits detection (last 24 hours)
- ✅ File changes tracking
- ✅ Branch comparison (ahead/behind)
- ✅ Git repository health checks
- ✅ Beautiful HTML email reports
- ✅ Automated daily scheduling

## Quick Start

### Option 1: GitHub Actions (Recommended for Cloud)

The workflow is already configured in `.github/workflows/daily-validation-report.yml`

**Setup:**

1. Ensure the scripts are executable:
   ```bash
   chmod +x scripts/validate_and_report.sh scripts/send_daily_report.py
   ```

2. (Optional) Configure your email in GitHub Secrets:
   ```bash
   # Go to Settings > Secrets and variables > Actions
   # Add: REPORT_EMAIL = your-email@gmail.com
   ```

3. The workflow will automatically run daily at 9 AM UTC

4. Check the workflow run results in Actions tab

**Manual Trigger:**
You can manually trigger the workflow from the Actions tab or using the GitHub CLI:
```bash
gh workflow run daily-validation-report.yml
```

### Option 2: Cron Job (Recommended for Local/Server)

Set up a cron job to run the scripts locally:

**Setup:**

1. Make scripts executable:
   ```bash
   chmod +x scripts/validate_and_report.sh scripts/send_daily_report.py
   ```

2. Create a wrapper script (e.g., `daily-report-cron.sh`):
   ```bash
   #!/bin/bash
   cd /path/to/x-devops
   REPORT_EMAIL="your-email@gmail.com" python3 scripts/send_daily_report.py
   ```

3. Make it executable:
   ```bash
   chmod +x daily-report-cron.sh
   ```

4. Add to crontab:
   ```bash
   crontab -e
   ```

5. Add this line (runs daily at 9 AM):
   ```cron
   0 9 * * * cd /path/to/x-devops && REPORT_EMAIL="your-email@gmail.com" bash scripts/validate_and_report.sh >> /var/log/repo-validation.log 2>&1
   ```

## Usage

### Generate a Report Manually

```bash
# Generate validation report
bash scripts/validate_and_report.sh

# The report is saved to /tmp/repo_validation_report.txt
cat /tmp/repo_validation_report.txt
```

### Generate Email Payload

```bash
# Generate email payload for Gmail
python3 scripts/send_daily_report.py --email your-email@gmail.com

# Or use environment variable
export REPORT_EMAIL="your-email@gmail.com"
python3 scripts/send_daily_report.py
```

### Advanced Options

```bash
# Custom repository path
REPO_PATH="/path/to/repo" python3 scripts/send_daily_report.py

# Custom email recipient
python3 scripts/send_daily_report.py --email user@example.com

# Custom base branch
BASE_BRANCH="develop" bash scripts/validate_and_report.sh
```

## Report Contents

Each validation report includes:

- **Repository Status**: Working directory state, uncommitted changes
- **New Commits**: Commits from the last 24 hours
- **Branch Comparison**: Commits ahead/behind the base branch
- **File Changes**: Modified files in the last 24 hours
- **Repository Health**: Git integrity checks
- **Summary**: Generation timestamp and status

## Sending to Gmail

### Using Gmail Drafts (Requires Gmail MCP Integration)

The system creates email drafts that you can review before sending:

```bash
# Generate the email payload
python3 scripts/send_daily_report.py --email your-email@gmail.com

# Use Claude Code's Gmail tools to send the draft:
# mcp__Gmail__create_draft(subject, to, htmlBody, body)
```

### Gmail Configuration Tips

1. **Enable Gmail API Access:**
   - Go to Google Cloud Console
   - Create an OAuth 2.0 application
   - Grant Gmail API access

2. **App Password (for SMTP):**
   - Enable 2-factor authentication
   - Generate an app-specific password
   - Use in your email client

## Environment Variables

- `REPO_PATH` - Path to the repository (default: current directory)
- `BASE_BRANCH` - Base branch to compare against (default: main)
- `REPORT_EMAIL` - Email recipient address (default: sathishkr.cs@gmail.com)

## Troubleshooting

### Script not executable
```bash
chmod +x scripts/validate_and_report.sh scripts/send_daily_report.py
```

### Git fetch fails in GitHub Actions
The workflow uses `fetch-depth: 0` to ensure full history is available.

### Report not generating
Check logs for errors:
```bash
bash scripts/validate_and_report.sh 2>&1
```

### Email not sending
Ensure:
- Email address is configured correctly
- Gmail MCP tools are available
- Gmail API is enabled in your account

## Customization

### Change Schedule

Edit `.github/workflows/daily-validation-report.yml`:

```yaml
schedule:
  - cron: '0 18 * * *'  # 6 PM UTC instead
```

Cron format: `minute hour day month day-of-week`

Common examples:
- `0 9 * * *` - 9 AM daily
- `0 18 * * *` - 6 PM daily
- `0 9 * * 1` - Every Monday at 9 AM
- `0 */12 * * *` - Every 12 hours

### Modify Report Template

Edit `scripts/send_daily_report.py` to customize the email HTML template.

### Add Custom Checks

Edit `scripts/validate_and_report.sh` to add additional validation checks.

## Security Notes

- Reports contain commit messages and file names (consider sensitivity)
- Email addresses should be protected as secrets in GitHub
- Git repositories with sensitive data should not use these public reports
- Consider using private email addresses or distribution lists

## Support

For issues with:

1. **Git commands**: Check your git configuration and repository permissions
2. **GitHub Actions**: See the workflow runs in the Actions tab
3. **Gmail**: Ensure Gmail API is enabled and credentials are configured
4. **Python scripts**: Check Python version and dependencies

## Integration with Claude Code

If using Claude Code on the web or CLI, you can integrate this with:

- **GitHub MCP Server**: Automatically run workflows and check results
- **Gmail MCP Server**: Send reports directly to your inbox
- **Session hooks**: Trigger reports on code changes
