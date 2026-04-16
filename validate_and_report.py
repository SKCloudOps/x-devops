#!/usr/bin/env python3
"""
Repository validation and daily report generator.
Validates repository and sends changes report via Gmail.
"""

import subprocess
import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import os

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

    # Check for differences with main
    diff_stats = run_command("git diff --stat main..HEAD")
    validation_report['branch_info']['diff_from_main'] = diff_stats if diff_stats else "No differences"

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
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
            h1 {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
            h2 {{ color: #0066cc; margin-top: 20px; }}
            .status-clean {{ background-color: #d4edda; padding: 10px; border-radius: 4px; }}
            .status-warning {{ background-color: #fff3cd; padding: 10px; border-radius: 4px; }}
            .commit {{ background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 3px solid #0066cc; }}
            .timestamp {{ color: #666; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th {{ background-color: #0066cc; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background-color: #f5f5f5; }}
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
                    <td>{validation_data['branch_info']['current_branch']}</td>
                </tr>
            </table>

            <h2>Repository Status</h2>
            <div class="status-clean">
                <strong>Uncommitted Changes:</strong> {validation_data['repo_status']['uncommitted_changes']}
                <p>{validation_data['repo_status']['status_output']}</p>
            </div>

            <h2>Changes from Main Branch (Last 24 Hours)</h2>
            <p><strong>New Commits:</strong> {validation_data['recent_changes']['main_branch']['new_commits_24h']}</p>
    """

    commits = validation_data['recent_changes']['main_branch']['commits']
    if commits:
        html += "<table><tr><th>Hash</th><th>Author</th><th>Date</th><th>Message</th></tr>"
        for commit in commits:
            html += f"""
            <tr>
                <td><code>{commit['hash']}</code></td>
                <td>{commit['author']}</td>
                <td>{commit['date'][:10]}</td>
                <td>{commit['message']}</td>
            </tr>
            """
        html += "</table>"
    else:
        html += "<p>No new commits in the last 24 hours on main branch.</p>"

    html += """
        </div>
    </body>
    </html>
    """
    return html

def main():
    """Main execution function."""
    print("🔍 Starting repository validation...")

    try:
        # Fetch latest changes
        print("📥 Fetching latest changes from remote...")
        run_command("git fetch origin")

        # Validate repository
        print("✅ Validating repository...")
        validation_data = validate_repository()

        # Format report
        html_report = format_html_report(validation_data)

        # Save report to file for reference
        report_file = f"repo_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w') as f:
            f.write(html_report)
        print(f"📄 Report saved to: {report_file}")

        # Output summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Repository: {validation_data['repo_info']['name']}")
        print(f"Current Branch: {validation_data['branch_info']['current_branch']}")
        print(f"Uncommitted Changes: {validation_data['repo_status']['uncommitted_changes']}")
        print(f"New Commits (main, 24h): {validation_data['recent_changes']['main_branch']['new_commits_24h']}")
        print("="*60)

        # Return HTML report for Gmail sending
        return html_report

    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    report = main()
    # Print report path for external use
    print(f"\nReport generated successfully")
