#!/usr/bin/env python3
"""
Daily repository validation and commit report sender.
Validates the repository, generates a report, and sends it via Gmail.

Usage:
    python3 daily_repo_report.py

Requirements:
    - .env file with GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD set
    - Gmail account with 2FA enabled
    - App-specific password generated at https://myaccount.google.com/apppasswords
"""

import subprocess
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def run_command(cmd: str) -> str:
    """Execute shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Command timeout"
    except Exception as e:
        return f"Error: {str(e)}"


def fetch_remote_changes() -> bool:
    """Fetch latest changes from remote repository."""
    print("📥 Fetching latest changes from remote...")
    result = run_command("git fetch origin")
    if "Error" not in result:
        print("✅ Fetch successful")
        return True
    print("⚠️  Fetch warning:", result)
    return False


def get_git_log(days: int = 1, branch: str = "main") -> List[Dict]:
    """Get commits from the last N days on specified branch."""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cmd = f"git log origin/{branch} --since='{since_date}' --oneline --format='%H|%an|%ae|%aI|%s|%b' --no-merges"
    output = run_command(cmd)

    commits = []
    if output and "Error" not in output:
        for line in output.split('\n'):
            if line.strip() and '|' in line:
                parts = line.split('|', 5)
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0][:7],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4],
                        'body': parts[5] if len(parts) > 5 else ''
                    })
    return commits


def get_file_changes(days: int = 1, branch: str = "main") -> Dict:
    """Get file statistics for the last N days."""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cmd = f"git diff --stat origin/main@{{'{since_date}'}}...origin/{branch}"
    output = run_command(cmd)
    return {'diff_stat': output if output and "Error" not in output else "No file changes"}


def validate_repository() -> Dict:
    """Comprehensive repository validation."""
    validation_report = {
        'timestamp': datetime.now().isoformat(),
        'repo_info': {},
        'repo_status': {},
        'branch_info': {},
        'recent_changes': {}
    }

    # Repository information
    repo_url = run_command("git config --get remote.origin.url")
    repo_name = repo_url.split('/')[-1].replace('.git', '')

    validation_report['repo_info'] = {
        'name': repo_name,
        'remote_url': repo_url,
        'local_path': os.getcwd()
    }

    # Check git status
    status = run_command("git status --short")
    uncommitted = status.split('\n') if status else []
    uncommitted = [line for line in uncommitted if line.strip()]

    validation_report['repo_status'] = {
        'uncommitted_changes_count': len(uncommitted),
        'uncommitted_changes': uncommitted if uncommitted else [],
        'status_message': 'Clean' if not uncommitted else f'{len(uncommitted)} uncommitted change(s)'
    }

    # Current branch
    current_branch = run_command("git rev-parse --abbrev-ref HEAD")
    validation_report['branch_info']['current_branch'] = current_branch

    # Get commit counts for main branch
    main_commits = get_git_log(days=1, branch="main")
    validation_report['recent_changes']['main_branch'] = {
        'new_commits_24h': len(main_commits),
        'commits': main_commits
    }

    # Get file changes
    file_changes = get_file_changes(days=1, branch="main")
    validation_report['recent_changes']['file_changes'] = file_changes

    # Get current branch commits if different from main
    if current_branch != "main" and current_branch != "HEAD":
        branch_commits = get_git_log(days=1, branch=current_branch)
        validation_report['recent_changes'][f'{current_branch}_branch'] = {
            'new_commits_24h': len(branch_commits),
            'commits': branch_commits
        }

    return validation_report


def format_uncommitted_changes(changes: List[str]) -> str:
    """Format uncommitted changes list."""
    if not changes:
        return ""
    html = "<div style='margin-top: 10px; background-color: rgba(255,255,255,0.5); padding: 10px; border-radius: 4px;'>"
    html += "<strong>Files:</strong><ul style='margin-left: 20px; margin-top: 5px;'>"
    for change in changes:
        html += f"<li><code>{change}</code></li>"
    html += "</ul></div>"
    return html


def format_commits(commits: List[Dict]) -> str:
    """Format commits list as HTML."""
    if not commits:
        return "<div class='empty-state'>No new commits in the last 24 hours</div>"
    html = "<div class='commit-list'>"
    for commit in commits:
        html += f"""
        <div class="commit">
            <span class="commit-hash">{commit['hash']}</span>
            <div class="commit-meta">
                <strong>{commit['author']}</strong> • {commit['date'][:10]}
            </div>
            <div class="commit-message">{commit['message']}</div>
        </div>
        """
    html += "</div>"
    return html


def format_html_report(validation_data: Dict) -> str:
    """Format validation report as professional HTML email."""
    has_changes = validation_data['repo_status']['uncommitted_changes_count'] > 0
    status_class = 'status-warning' if has_changes else 'status-clean'
    status_icon = '⚠️' if has_changes else '✅'

    uncommitted_html = format_uncommitted_changes(validation_data['repo_status']['uncommitted_changes'])
    commits_html = format_commits(validation_data['recent_changes']['main_branch']['commits'])

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif; background-color: #f5f5f5; color: #333; }}
            .container {{ max-width: 900px; margin: 0 auto; background-color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%); color: white; padding: 30px 20px; text-align: center; }}
            .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
            .header p {{ font-size: 14px; opacity: 0.9; }}
            .content {{ padding: 30px 20px; }}
            .section {{ margin-bottom: 30px; }}
            .section h2 {{ color: #0066cc; font-size: 18px; margin-bottom: 15px; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
            .info-box {{ background-color: #f9f9f9; padding: 15px; border-radius: 6px; border-left: 4px solid #0066cc; }}
            .info-box strong {{ color: #0066cc; display: block; margin-bottom: 5px; }}
            .info-box span {{ word-break: break-all; }}
            .status-clean {{ background-color: #d4edda; border-color: #28a745; color: #155724; }}
            .status-warning {{ background-color: #fff3cd; border-color: #ffc107; color: #856404; }}
            .status-box {{ padding: 15px; border-radius: 6px; border-left: 4px solid; margin-bottom: 20px; }}
            .commit-list {{ background-color: #f9f9f9; border-radius: 6px; overflow: hidden; }}
            .commit {{ padding: 15px; border-bottom: 1px solid #e0e0e0; }}
            .commit:last-child {{ border-bottom: none; }}
            .commit-hash {{ color: #0066cc; font-family: 'Courier New', monospace; font-weight: bold; }}
            .commit-meta {{ font-size: 12px; color: #666; margin: 5px 0; }}
            .commit-message {{ color: #333; margin: 8px 0 0 0; }}
            .empty-state {{ color: #999; font-style: italic; padding: 20px; text-align: center; }}
            .footer {{ background-color: #f9f9f9; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666; }}
            .timestamp {{ color: #666; font-size: 12px; }}
            code {{ background-color: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Daily Repository Report</h1>
                <p>Generated on {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}</p>
            </div>

            <div class="content">
                <!-- Repository Info Section -->
                <div class="section">
                    <h2>📁 Repository Information</h2>
                    <div class="info-grid">
                        <div class="info-box">
                            <strong>Repository:</strong>
                            <span>{validation_data['repo_info']['name']}</span>
                        </div>
                        <div class="info-box">
                            <strong>Current Branch:</strong>
                            <span><code>{validation_data['branch_info']['current_branch']}</code></span>
                        </div>
                        <div class="info-box">
                            <strong>Remote URL:</strong>
                            <span><code>{validation_data['repo_info']['remote_url']}</code></span>
                        </div>
                        <div class="info-box">
                            <strong>Local Path:</strong>
                            <span><code>{validation_data['repo_info']['local_path']}</code></span>
                        </div>
                    </div>
                </div>

                <!-- Repository Status Section -->
                <div class="section">
                    <h2>{status_icon} Repository Status</h2>
                    <div class="status-box {status_class}">
                        <strong>Working Directory Status:</strong> {validation_data['repo_status']['status_message']}
                        <p>Uncommitted Changes: <strong>{validation_data['repo_status']['uncommitted_changes_count']}</strong></p>
                        {uncommitted_html}
                    </div>
                </div>

                <!-- Main Branch Changes Section -->
                <div class="section">
                    <h2>📝 Main Branch Changes (Last 24 Hours)</h2>
                    <p>Total new commits: <strong>{validation_data['recent_changes']['main_branch']['new_commits_24h']}</strong></p>
                    {commits_html}
                </div>
            </div>

            <div class="footer">
                <p>Generated by Daily Repository Report System</p>
                <p class="timestamp">Timestamp: {validation_data['timestamp']}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_email(recipient: str, subject: str, html_body: str, sender_email: str, app_password: str) -> bool:
    """Send email via Gmail SMTP."""
    try:
        clean_password = app_password.replace(" ", "")

        # Validate emails
        if not sender_email or "@" not in sender_email:
            raise ValueError(f"Invalid sender email: {sender_email}")
        if not recipient or "@" not in recipient:
            raise ValueError(f"Invalid recipient email: {recipient}")

        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient

        # Attach HTML content
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

    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail authentication failed!")
        print("   Troubleshooting steps:")
        print("   1. Ensure GMAIL_SENDER_EMAIL is your full Gmail address")
        print("   2. Generate a new app password at: https://myaccount.google.com/apppasswords")
        print("   3. Ensure 2FA is enabled on your Google account")
        print("   4. Copy the 16-character password (remove spaces) as GMAIL_APP_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        return False


def main():
    """Main execution function."""
    print("=" * 70)
    print("🚀 Daily Repository Validation and Report Generator")
    print("=" * 70)

    try:
        # Fetch latest changes
        if not fetch_remote_changes():
            print("⚠️  Warning: Could not fetch remote changes, continuing with local data...")

        # Validate repository
        print("✅ Validating repository...")
        validation_data = validate_repository()

        # Print summary
        print("\n" + "=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Repository: {validation_data['repo_info']['name']}")
        print(f"Current Branch: {validation_data['branch_info']['current_branch']}")
        print(f"Uncommitted Changes: {validation_data['repo_status']['uncommitted_changes_count']}")
        print(f"New Commits on Main (24h): {validation_data['recent_changes']['main_branch']['new_commits_24h']}")
        print("=" * 70)

        # Get Gmail credentials
        sender_email = os.getenv('GMAIL_SENDER_EMAIL', '').strip()
        app_password = os.getenv('GMAIL_APP_PASSWORD', '').strip()
        recipient_email = os.getenv('GMAIL_RECIPIENT_EMAIL', '').strip()

        if not recipient_email:
            recipient_email = 'sathishkrcs@gmail.com'
            print(f"⚠️  Using default recipient: {recipient_email}")

        # Check for credentials
        if not sender_email or not app_password:
            print("\n❌ Gmail credentials not configured!")
            print("\nSetup instructions:")
            print("1. Copy .env.example to .env:")
            print("   cp .env.example .env")
            print("\n2. Edit .env and add your credentials:")
            print("   GMAIL_SENDER_EMAIL=your-email@gmail.com")
            print("   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
            print("   GMAIL_RECIPIENT_EMAIL=recipient@example.com")
            print("\n3. Generate Gmail app password at: https://myaccount.google.com/apppasswords")
            print("   (Requires 2FA enabled)")
            return False

        # Format and send report
        print(f"\n📝 Generating HTML report...")
        html_report = format_html_report(validation_data)

        # Save report locally for reference
        report_file = f"reports/repo_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        os.makedirs("reports", exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(html_report)
        print(f"💾 Report saved to: {report_file}")

        # Send email
        subject = f"🔍 Daily Repo Report - {validation_data['repo_info']['name']} ({datetime.now().strftime('%Y-%m-%d')})"
        print(f"\n📧 Sending report to {recipient_email}...")

        if send_email(recipient_email, subject, html_report, sender_email, app_password):
            print("\n" + "=" * 70)
            print("✅ SUCCESS: Repository validation and report complete!")
            print("=" * 70)
            return True
        else:
            print("\n" + "=" * 70)
            print("⚠️  Report generated but email sending failed")
            print("=" * 70)
            return False

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
