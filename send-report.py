#!/usr/bin/env python3
"""
Send daily repository validation report via Gmail.
This script reads the latest validation report and sends it via email.
"""

import os
import sys
from datetime import datetime

def send_email_draft(recipient_email, subject, body_content):
    """
    Note: This is a placeholder for Gmail MCP integration.
    In a production environment, this would use the mcp__Gmail__create_draft tool.

    The actual sending would be handled by Claude's Gmail MCP tools.
    """
    print(f"Email Report Ready to Send")
    print(f"To: {recipient_email}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body_content}")
    print("\n" + "="*80)
    return True

def main():
    report_file = "/tmp/latest-repo-report.txt"
    recipient = "sathishkr.cs@gmail.com"

    # Read the latest report
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            report_content = f.read()
    else:
        print(f"Error: Report file not found at {report_file}")
        sys.exit(1)

    # Prepare email
    subject = f"Daily Repository Validation Report - x-devops - {datetime.now().strftime('%Y-%m-%d')}"

    # Format email body
    email_body = f"""
Repository Validation Report

{report_content}

---
This is an automated daily report.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Repository: x-devops
"""

    # Send email (via Gmail MCP)
    if send_email_draft(recipient, subject, email_body):
        print(f"✓ Report ready to send to {recipient}")
        print(f"✓ Subject: {subject}")
    else:
        print("✗ Failed to send email")
        sys.exit(1)

if __name__ == "__main__":
    main()
