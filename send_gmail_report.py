#!/usr/bin/env python3
"""
Send validation report via Gmail SMTP.
Requires Gmail app password to be set in environment or .env file.
"""

import subprocess
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_command(cmd: str) -> str:
    """Execute shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def get_git_log(days: int = 1, branch: str = "main") -> List[Dict]:
    """Get commits from the last N days."""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cmd = f"git log origin/{branch} --since='{since_date}' --oneline --format='%H|%an|%ae|%aI|%s'"
    output = run_command(cmd)

    commits = []
    if output and "Error" not in output:
        for line in output.split('\n'):
            if line.strip():
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0][:7],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })
    return commits

def validate_repository() -> Dict:
    """Validate repository integrity and configuration."""
    validation_report = {
        'timestamp': datetime.now().isoformat(),
        'repo_status': {},
        'branch_info': {},
        'recent_changes': {}
    }

    # Check git status
    status = run_command("git status --short")
    validation_report['repo_status']['uncommitted_changes'] = len(status.split('\n')) if status else 0
    validation_report['repo_status']['status_output'] = status if status else "Clean working directory"

    # Check current branch
    current_branch = run_command("git rev-parse --abbrev-ref HEAD")
    validation_report['branch_info']['current_branch'] = current_branch

    # Get main branch info
    main_commits = get_git_log(days=1, branch="main")
    validation_report['recent_changes']['main_branch'] = {
        'new_commits_24h': len(main_commits),
        'commits': main_commits
    }

    # Repository info
    repo_name = run_command("git config --get remote.origin.url").split('/')[-1]
    validation_report['repo_info'] = {
        'name': repo_name,
        'remote_url': run_command("git config --get remote.origin.url")
    }

    return validation_report

def format_html_report(validation_data: Dict) -> str:
    """Format validation report as HTML email."""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
            h2 {{ color: #0066cc; margin-top: 20px; }}
            .status-clean {{ background-color: #d4edda; padding: 10px; border-radius: 4px; }}
            .timestamp {{ color: #666; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th {{ background-color: #0066cc; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background-color: #f5f5f5; }}
            code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Repository Validation Report</h1>
            <p class="timestamp">Generated: {validation_data['timestamp']}</p>

            <h2>Repository Info</h2>
            <table>
                <tr>
                    <td><strong>Repository:</strong></td>
                    <td>{validation_data['repo_info']['name']}</td>
                </tr>
                <tr>
                    <td><strong>Current Branch:</strong></td>
                    <td><code>{validation_data['branch_info']['current_branch']}</code></td>
                </tr>
            </table>

            <h2>Repository Status</h2>
            <div class="status-clean">
                <strong>Uncommitted Changes:</strong> {validation_data['repo_status']['uncommitted_changes']}<br>
                <strong>Status:</strong> {validation_data['repo_status']['status_output']}
            </div>

            <h2>Changes from Main Branch (Last 24 Hours)</h2>
            <p><strong>Total New Commits:</strong> {validation_data['recent_changes']['main_branch']['new_commits_24h']}</p>
    """

    commits = validation_data['recent_changes']['main_branch']['commits']
    if commits:
        html += "<table><tr><th>Hash</th><th>Author</th><th>Date</th><th>Message</th></tr>"
        for commit in commits:
            html += f"""<tr>
                <td><code>{commit['hash']}</code></td>
                <td>{commit['author']}</td>
                <td>{commit['date'][:10]}</td>
                <td>{commit['message']}</td>
            </tr>
            """
        html += "</table>"
    else:
        html += "<p><em>No new commits in the last 24 hours on main branch.</em></p>"

    html += """
        </div>
    </body>
    </html>
    """
    return html

def send_via_gmail(recipient: str, subject: str, html_body: str, sender_email: str, app_password: str) -> bool:
    """Send email via Gmail SMTP."""
    try:
        # Strip spaces from app password (Gmail generates passwords with spaces)
        clean_password = app_password.replace(" ", "")

        # Validate email addresses
        if not sender_email or "@" not in sender_email:
            raise ValueError(f"Invalid sender email: {sender_email}")
        if not recipient or "@" not in recipient:
            raise ValueError(f"Invalid recipient email: {recipient}")

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient

        # Attach HTML part
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        # Send via Gmail SMTP
        print(f"📧 Connecting to Gmail SMTP server...")
        print(f"   Sender: {sender_email}")
        print(f"   Recipient: {recipient}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, clean_password)
            server.sendmail(sender_email, recipient, message.as_string())

        print(f"✅ Email sent successfully to {recipient}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed!")
        print(f"   Check that:")
        print(f"   1. GMAIL_SENDER_EMAIL is correct")
        print(f"   2. GMAIL_APP_PASSWORD is the 16-char app password (not your regular password)")
        print(f"   3. 2-factor authentication is enabled on the Google account")
        print(f"   4. The app password hasn't been revoked")
        print(f"   Error: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution function."""
    print("🔍 Starting repository validation and email sending...")

    try:
        # Fetch latest changes
        print("📥 Fetching latest changes from remote...")
        run_command("git fetch origin")

        # Validate repository
        print("✅ Validating repository...")
        validation_data = validate_repository()

        # Format report
        html_report = format_html_report(validation_data)
        subject = f"Daily Repo Report - {validation_data['repo_info']['name']} ({datetime.now().strftime('%Y-%m-%d')})"

        # Output summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Repository: {validation_data['repo_info']['name']}")
        print(f"Current Branch: {validation_data['branch_info']['current_branch']}")
        print(f"Uncommitted Changes: {validation_data['repo_status']['uncommitted_changes']}")
        print(f"New Commits (main, 24h): {validation_data['recent_changes']['main_branch']['new_commits_24h']}")
        print("="*60)

        # Check for Gmail credentials
        sender_email = os.getenv('GMAIL_SENDER_EMAIL')
        app_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient_email = os.getenv('GMAIL_RECIPIENT_EMAIL', 'sathishkrcs@gmail.com')

        if not sender_email or not app_password:
            print("\n⚠️  Gmail credentials not found in environment variables.")
            print("To send reports via Gmail, please set:")
            print("  - GMAIL_SENDER_EMAIL: Your Gmail address")
            print("  - GMAIL_APP_PASSWORD: Gmail app-specific password")
            print("  - GMAIL_RECIPIENT_EMAIL: Recipient email (optional, defaults to sathishkrcs@gmail.com)")
            print("\nSetup instructions:")
            print("1. Enable 2-factor authentication on your Google account")
            print("2. Create an app password: https://myaccount.google.com/apppasswords")
            print("3. Set environment variables in .env file or export them")
            return

        # Send email
        print(f"\n📧 Sending report to {recipient_email}...")
        success = send_via_gmail(recipient_email, subject, html_report, sender_email, app_password)

        if success:
            print("✅ Report sent successfully!")
        else:
            print("❌ Failed to send report")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
