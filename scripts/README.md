# Repository Validation & Reporting Scripts

This directory contains scripts for daily repository validation and automated email reporting.

## Scripts Overview

### `validate_and_report.sh`

**Purpose**: Validates the repository and generates a detailed report.

**Features**:
- Repository status checking (working directory cleanliness)
- New commits detection (last 24 hours)
- Branch comparison (ahead/behind base branch)
- File changes tracking
- Git repository health validation

**Usage**:
```bash
bash validate_and_report.sh
```

**Environment Variables**:
- `REPO_PATH` - Path to the repository (default: `.`)
- `BASE_BRANCH` - Base branch for comparison (default: `main`)

**Output**:
- Generates report file at `/tmp/repo_validation_report.txt`
- Prints the path to the report file

**Example**:
```bash
REPO_PATH=/home/user/x-devops BASE_BRANCH=main bash validate_and_report.sh
```

---

### `send_daily_report.py`

**Purpose**: Generates email-ready payload from the validation report.

**Features**:
- Reads validation report
- Generates HTML-formatted email content
- Creates JSON payload for Gmail integration
- Supports custom recipients
- Beautiful email template with styling

**Usage**:
```bash
python3 send_daily_report.py [OPTIONS]
```

**Options**:
- `--email RECIPIENT` - Email recipient address
- `--repo PATH` - Repository path

**Environment Variables**:
- `REPORT_EMAIL` - Email recipient (default: `sathishkr.cs@gmail.com`)
- `REPO_PATH` - Repository path (default: `.`)

**Output**:
- JSON payload with email subject, HTML body, and plain text body
- Suitable for use with Gmail MCP tools

**Example**:
```bash
REPORT_EMAIL="user@example.com" python3 send_daily_report.py

# Or with arguments
python3 send_daily_report.py --email user@example.com --repo /path/to/repo
```

---

### `setup-cron.sh`

**Purpose**: Helper script to set up cron-based scheduling for automated reports.

**Features**:
- Validates script permissions
- Generates cron entry
- Provides installation instructions
- Sets up logging

**Usage**:
```bash
bash setup-cron.sh
```

**Environment Variables**:
- `REPORT_EMAIL` - Email for reports (default: `sathishkr.cs@gmail.com`)
- `CRON_HOUR` - Hour to run (default: `9`)
- `CRON_MINUTE` - Minute to run (default: `0`)
- `LOG_DIR` - Directory for logs (default: `/var/log`)

**Example**:
```bash
REPORT_EMAIL="user@example.com" CRON_HOUR=18 bash setup-cron.sh
```

---

## Quick Start

### One-Time Report
```bash
# Generate validation report
bash validate_and_report.sh

# View the report
cat /tmp/repo_validation_report.txt

# Prepare for email
python3 send_daily_report.py --email your-email@gmail.com
```

### Automated Daily Reports (GitHub Actions)

The workflow in `.github/workflows/daily-validation-report.yml` automatically runs daily at 9 AM UTC.

### Automated Daily Reports (Cron)

```bash
# Set up cron scheduling
bash scripts/setup-cron.sh

# Follow the instructions printed by the script
crontab -e
```

## Output Examples

### Validation Report

```
===============================================
Repository Validation Report
===============================================
Date: 2026-06-13 15:02:54
Repository: x-devops
Current Branch: claude/gifted-ride-glvbh4
Base Branch: main

=== Repository Status ===
✓ Working directory is clean

=== New Commits (last 24 hours) ===
No new commits in the last 24 hours

=== Comparison with Base Branch (main) ===
Commits ahead of base: 0
Commits behind base: 0
```

### Email Payload (JSON)

```json
{
  "subject": "Daily Repository Validation Report - 2026-06-13",
  "to": ["your-email@gmail.com"],
  "htmlBody": "...(formatted HTML)...",
  "body": "...(plain text)..."
}
```

## Integration with Claude Code

These scripts integrate with:

1. **GitHub MCP Server** - Run workflows and check results
2. **Gmail MCP Server** - Send reports to your inbox
3. **Claude Code CLI** - Manual report generation and sending

### Using with Claude Code

```bash
# Generate report and create Gmail draft
python3 scripts/send_daily_report.py --email your-email@gmail.com

# Then use Claude Code to send with Gmail MCP tools
# mcp__Gmail__create_draft(payload)
```

## Customization

### Change Report Schedule

Edit `.github/workflows/daily-validation-report.yml`:

```yaml
schedule:
  - cron: '0 18 * * *'  # Change from 9 AM to 6 PM
```

### Add Custom Validation Checks

Edit `validate_and_report.sh` to add checks (e.g., test results, linting).

### Modify Email Template

Edit `send_daily_report.py` function `prepare_email_content()` to customize the HTML template.

## Troubleshooting

### Script not found
```bash
# Make sure you're in the repository root or scripts directory
cd /path/to/x-devops
bash scripts/validate_and_report.sh
```

### Permission denied
```bash
chmod +x scripts/validate_and_report.sh scripts/send_daily_report.py
```

### Report file not found
- Ensure `/tmp` directory is writable
- Check disk space: `df -h`
- Review script output for errors

### Email not sending
- Verify email address is correct
- Check Gmail MCP tools are available
- Ensure Gmail API is enabled in your Google account

## Requirements

- **Bash 4.0+** for shell scripts
- **Python 3.6+** for Python scripts
- **Git** for repository validation
- **Cron daemon** for scheduled execution (optional)
- **Gmail MCP tools** for email integration (optional)

## Security

- Report contains commit messages and file names
- Email addresses should be kept private
- Use GitHub Secrets for sensitive email addresses
- Consider git history sensitivity before sharing reports

## Support

For detailed setup instructions, see `../VALIDATION_REPORT_SETUP.md`
