#!/usr/bin/env python3
"""
Verify that the daily validation report setup is configured correctly.
This script checks:
1. All required Python scripts exist
2. Requirements.txt has necessary dependencies
3. GitHub Actions workflow is configured
4. Git repository is properly configured
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and return status."""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_git_config():
    """Check git repository configuration."""
    print("\n📋 Git Configuration:")

    try:
        remote_url = subprocess.run(
            "git config --get remote.origin.url",
            shell=True, capture_output=True, text=True
        ).stdout.strip()
        current_branch = subprocess.run(
            "git rev-parse --abbrev-ref HEAD",
            shell=True, capture_output=True, text=True
        ).stdout.strip()

        print(f"  ✅ Remote URL: {remote_url}")
        print(f"  ✅ Current Branch: {current_branch}")
        return True
    except Exception as e:
        print(f"  ❌ Error checking git config: {e}")
        return False

def check_python_dependencies():
    """Check if required Python packages are available."""
    print("\n📦 Python Dependencies:")

    required_packages = {
        'anthropic': 'Claude API client',
        'tweepy': 'Twitter API client',
        'python-dotenv': 'Environment variable loader',
        'requests': 'HTTP library'
    }

    all_present = True
    for package, description in required_packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}: {description}")
        except ImportError:
            print(f"  ❌ {package}: Missing - run 'pip install {package}'")
            all_present = False

    return all_present

def check_github_workflow():
    """Check GitHub Actions workflow configuration."""
    print("\n⚙️  GitHub Actions Workflow:")

    workflow_path = ".github/workflows/daily-validation-report.yml"

    if os.path.exists(workflow_path):
        print(f"  ✅ Workflow file exists: {workflow_path}")

        with open(workflow_path, 'r') as f:
            content = f.read()

        checks = {
            'schedule': 'Daily schedule configured',
            'GMAIL_SENDER_EMAIL': 'Gmail sender email secret',
            'GMAIL_APP_PASSWORD': 'Gmail app password secret',
            'GMAIL_RECIPIENT_EMAIL': 'Gmail recipient email secret',
            'send_gmail_report.py': 'Report sending script'
        }

        for check, description in checks.items():
            if check in content:
                print(f"    ✅ {description}")
            else:
                print(f"    ⚠️  {description} - might need configuration")

        return True
    else:
        print(f"  ❌ Workflow file missing: {workflow_path}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🔍 Daily Validation Report Setup Verification")
    print("=" * 60)

    checks_passed = []

    # Check Python scripts
    print("\n📄 Required Python Scripts:")
    scripts = {
        'validate_and_report.py': 'Repository validation',
        'send_gmail_report.py': 'Gmail report sender',
        'send_validation_report.py': 'Report formatter'
    }

    scripts_ok = True
    for script, description in scripts.items():
        if check_file_exists(script, description):
            checks_passed.append(script)
        else:
            scripts_ok = False

    # Check configuration files
    print("\n⚙️  Configuration Files:")
    configs = {
        'requirements.txt': 'Python dependencies',
        '.gitignore': 'Git ignore rules'
    }

    configs_ok = True
    for config, description in configs.items():
        if check_file_exists(config, description):
            checks_passed.append(config)
        else:
            configs_ok = False

    # Check documentation
    print("\n📚 Documentation:")
    docs = {
        'SETUP_DAILY_REPORTS.md': 'Setup instructions',
        'DAILY_REPORTS_SETUP.md': 'Legacy setup guide'
    }

    docs_ok = True
    for doc, description in docs.items():
        if check_file_exists(doc, description):
            checks_passed.append(doc)
        else:
            docs_ok = False

    # Check git configuration
    git_ok = check_git_config()

    # Check Python dependencies
    deps_ok = check_python_dependencies()

    # Check GitHub workflow
    workflow_ok = check_github_workflow()

    # Print summary
    print("\n" + "=" * 60)
    print("📊 SETUP STATUS SUMMARY")
    print("=" * 60)

    summary = {
        'Python Scripts': '✅ Ready' if scripts_ok else '❌ Missing',
        'Configuration': '✅ Ready' if configs_ok else '❌ Missing',
        'Documentation': '✅ Ready' if docs_ok else '⚠️  Partial',
        'Git Repository': '✅ Configured' if git_ok else '❌ Error',
        'Python Dependencies': '✅ Installed' if deps_ok else '❌ Missing',
        'GitHub Actions': '✅ Configured' if workflow_ok else '❌ Missing'
    }

    for item, status in summary.items():
        print(f"{item}: {status}")

    print("\n" + "=" * 60)
    print("🚀 NEXT STEPS")
    print("=" * 60)

    if all([scripts_ok, configs_ok, git_ok, workflow_ok]):
        print("""
✅ Your repository is ready for daily validation reports!

To enable automated reports:

1. Read the setup guide:
   cat SETUP_DAILY_REPORTS.md

2. Follow these steps:
   - Enable 2-Factor Authentication on Google Account
   - Create Gmail App Password
   - Add GitHub Secrets (GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD, GMAIL_RECIPIENT_EMAIL)
   - Test by running the workflow manually

3. Reports will automatically run at 9 AM UTC daily!

For more details, see: SETUP_DAILY_REPORTS.md
        """)
    else:
        print("""
⚠️  Some components are missing or not configured.

Please review the items marked with ❌ above and:
1. Install missing Python dependencies: pip install -r requirements.txt
2. Ensure all required scripts are present
3. Check GitHub Actions workflow configuration

For help, see: SETUP_DAILY_REPORTS.md
        """)

    print("=" * 60)

if __name__ == "__main__":
    main()
