#!/usr/bin/env python3
"""
Generate repository validation report and send via Gmail.
This script generates a daily report of new commits and changes.
"""

import json
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def generate_report():
    """Generate the repository validation report."""
    report = []
    report.append("=== Daily Repository Validation Report ===")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")

    # Repository info
    repo_name = run_command("basename $(pwd)")
    current_branch = run_command("git rev-parse --abbrev-ref HEAD")
    base_branch = "main"

    report.append(f"Repository: {repo_name}")
    report.append(f"Current Branch: {current_branch}")
    report.append(f"Base Branch: {base_branch}")
    report.append("")

    # Fetch latest
    run_command("git fetch origin")

    # New commits in base branch
    report.append("=== NEW COMMITS IN BASE BRANCH ===")
    commits = run_command(f"git log origin/{base_branch} --oneline -10")
    report.append(commits)
    report.append("")

    # Changes comparison
    report.append("=== CHANGES COMPARISON ===")
    files_changed = run_command(f"git diff --name-status origin/{base_branch}..HEAD")
    if files_changed:
        report.append(files_changed)
    else:
        report.append("No differences from base branch")
    report.append("")

    # Commit stats
    report.append("=== COMMIT STATISTICS ===")
    commits_ahead = run_command(f"git rev-list --count origin/{base_branch}..HEAD")
    report.append(f"Commits ahead of {base_branch}: {commits_ahead}")
    report.append("")

    # Repository status
    report.append("=== REPOSITORY STATUS ===")
    status = run_command("git status --short")
    report.append(status if status else "Working directory clean")
    report.append("")

    # Branch info
    report.append("=== BRANCH INFO ===")
    branches = run_command("git branch -vv")
    report.append(branches)

    return "\n".join(report)

def send_gmail_draft(report_content, recipient_email):
    """
    Send report via Gmail by creating a draft.
    Note: This would require Gmail API integration or manual sending.
    For now, we print instructions.
    """
    subject = f"Daily Repository Report - {datetime.now().strftime('%Y-%m-%d')}"

    email_data = {
        "to": [recipient_email],
        "subject": subject,
        "body": report_content
    }

    print("\n" + "="*60)
    print("EMAIL READY TO SEND:")
    print("="*60)
    print(f"To: {recipient_email}")
    print(f"Subject: {subject}")
    print("-"*60)
    print(report_content)
    print("-"*60)
    print("\nTo send this via Gmail, you can:")
    print("1. Create a draft manually with the above content")
    print("2. Use Gmail API with a service account")
    print("3. Configure an email service like SendGrid")
    print("="*60)

    # Return JSON for potential Claude Code integration
    return json.dumps(email_data, indent=2)

if __name__ == "__main__":
    email = "sathishkr.cs@gmail.com"

    print("Generating repository validation report...")
    report = generate_report()

    print("\n" + report)

    print("\nSending report to Gmail...")
    email_json = send_gmail_draft(report, email)
