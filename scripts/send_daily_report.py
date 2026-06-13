#!/usr/bin/env python3
"""
Daily Repository Validation Report Generator and Emailer
Validates the repository and sends daily reports via Gmail
"""

import subprocess
import json
import sys
from datetime import datetime
import os

def run_validation_script():
    """Run the validation script and return the report path"""
    try:
        repo_path = os.environ.get('REPO_PATH', '.')
        script_path = os.path.join(os.path.dirname(__file__), 'validate_and_report.sh')

        result = subprocess.run(
            ['bash', script_path],
            env={**os.environ, 'REPO_PATH': repo_path},
            capture_output=True,
            text=True,
            check=True
        )

        report_path = result.stdout.strip()
        return report_path
    except subprocess.CalledProcessError as e:
        print(f"Error running validation script: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def read_report(report_path):
    """Read the validation report"""
    try:
        with open(report_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Report file not found: {report_path}", file=sys.stderr)
        sys.exit(1)

def prepare_email_content(report_content):
    """Prepare email subject and body"""
    date = datetime.now().strftime('%Y-%m-%d')
    subject = f"Daily Repository Validation Report - {date}"

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; border-left: 4px solid #0066cc; overflow-x: auto; }}
            h1 {{ color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
            .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .timestamp {{ color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>Daily Repository Validation Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <div class="summary">
            <p>This is your daily automated repository validation report. Find details below:</p>
        </div>
        <pre>{report_content}</pre>
        <p style="margin-top: 30px; color: #999; font-size: 0.9em;">
            This is an automated report. Do not reply to this email.
        </p>
    </body>
    </html>
    """

    return subject, html_body, report_content

def create_gmail_payload(subject, html_body, body, recipient):
    """Create the payload for Gmail draft API"""
    return {
        "subject": subject,
        "to": [recipient],
        "htmlBody": html_body,
        "body": body
    }

def generate_report(recipient_email=None):
    """Main function to generate and prepare the report"""
    if recipient_email is None:
        recipient_email = os.environ.get('REPORT_EMAIL', 'sathishkr.cs@gmail.com')

    print("🔍 Running repository validation...", file=sys.stderr)
    report_path = run_validation_script()

    print(f"📄 Reading report from {report_path}...", file=sys.stderr)
    report_content = read_report(report_path)

    print("✉️  Preparing email content...", file=sys.stderr)
    subject, html_body, body = prepare_email_content(report_content)

    payload = create_gmail_payload(subject, html_body, body, recipient_email)

    # Output the payload as JSON for use with Gmail MCP tools
    print(json.dumps({
        "action": "create_gmail_draft",
        "payload": payload,
        "report_path": report_path
    }, indent=2))

    return payload, report_path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate and send daily repository validation report')
    parser.add_argument('--email', help='Email recipient (default: REPORT_EMAIL env var or sathishkr.cs@gmail.com)')
    parser.add_argument('--repo', help='Repository path (default: current directory)')

    args = parser.parse_args()

    if args.repo:
        os.environ['REPO_PATH'] = args.repo

    payload, report_path = generate_report(args.email)

    print(f"\n✅ Report preparation complete!", file=sys.stderr)
    print(f"📧 To send this report via Gmail, use the mcp__Gmail__create_draft tool with the following payload:", file=sys.stderr)
    print(f"   Subject: {payload['subject']}", file=sys.stderr)
    print(f"   To: {payload['to'][0]}", file=sys.stderr)
