#!/usr/bin/env python3
"""
Verify the daily validation report setup.
Checks all prerequisites and configurations.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_git_setup():
    """Check git repository setup."""
    try:
        result = subprocess.run("git config --get remote.origin.url",
                              shell=True, capture_output=True, text=True)
        remote = result.stdout.strip()
        print(f"✓ Git remote: {remote}")

        result = subprocess.run("git rev-parse --abbrev-ref HEAD",
                              shell=True, capture_output=True, text=True)
        branch = result.stdout.strip()
        print(f"✓ Current branch: {branch}")
        return True
    except Exception as e:
        print(f"✗ Git setup error: {e}")
        return False

def check_dependencies():
    """Check required Python packages."""
    required = ['dotenv', 'smtplib']  # smtplib is built-in

    try:
        import dotenv
        print(f"✓ python-dotenv installed")
    except ImportError:
        print(f"✗ python-dotenv not installed")
        print("  Run: pip install python-dotenv")
        return False

    # smtplib is built-in
    print(f"✓ smtplib (built-in) available")
    return True

def check_env_file():
    """Check .env file configuration."""
    env_path = Path(".env")

    if not env_path.exists():
        print(f"✗ .env file not found at {env_path.absolute()}")
        print(f"  Action: Create .env file with Gmail credentials")
        print(f"  See: SETUP_GUIDE.md for instructions")
        return False

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    sender = os.getenv('GMAIL_SENDER_EMAIL', '').strip()
    password = os.getenv('GMAIL_APP_PASSWORD', '').strip()
    recipient = os.getenv('GMAIL_RECIPIENT_EMAIL', '').strip()

    if not sender:
        print(f"✗ GMAIL_SENDER_EMAIL not configured in .env")
        return False
    print(f"✓ GMAIL_SENDER_EMAIL: {sender}")

    if not password:
        print(f"✗ GMAIL_APP_PASSWORD not configured in .env")
        return False
    print(f"✓ GMAIL_APP_PASSWORD: {'*' * len(password)}")

    if not recipient:
        print(f"✗ GMAIL_RECIPIENT_EMAIL not configured in .env")
        return False
    print(f"✓ GMAIL_RECIPIENT_EMAIL: {recipient}")

    return True

def check_scripts():
    """Check required scripts exist."""
    scripts = [
        'send_gmail_report.py',
        'validate_and_report.py'
    ]

    for script in scripts:
        path = Path(script)
        if path.exists():
            print(f"✓ {script} exists")
        else:
            print(f"✗ {script} not found")
            return False

    return True

def check_github_workflow():
    """Check GitHub Actions workflow."""
    workflow_path = Path(".github/workflows/daily-validation-report.yml")

    if workflow_path.exists():
        print(f"✓ GitHub Actions workflow exists: {workflow_path}")
        return True
    else:
        print(f"✗ GitHub Actions workflow not found")
        return False

def print_summary(all_checks):
    """Print verification summary."""
    print("\n" + "="*60)
    print("SETUP VERIFICATION SUMMARY")
    print("="*60)

    if all(all_checks.values()):
        print("\n✅ All checks passed!")
        print("\nYou're ready to use the validation report system.")
        print("Next steps:")
        print("1. Test the setup: python3 send_gmail_report.py")
        print("2. Set up automation (cron or GitHub Actions)")
        print("\nFor detailed instructions, see: SETUP_GUIDE.md")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("\nFor help, see: SETUP_GUIDE.md")

def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("DAILY VALIDATION REPORT - SETUP VERIFICATION")
    print("="*60 + "\n")

    checks = {
        'Python Version': check_python_version(),
        'Git Setup': check_git_setup(),
        'Dependencies': check_dependencies(),
        'Scripts': check_scripts(),
        'GitHub Workflow': check_github_workflow(),
        'Environment Configuration': check_env_file(),
    }

    print_summary(checks)
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
