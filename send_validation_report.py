#!/usr/bin/env python3
"""
Script to generate and prepare validation report for Gmail sending.
This script generates the validation report and outputs it in a format
ready to be sent via Gmail MCP tools.
"""

import subprocess
import json
from datetime import datetime, timedelta
from typing import List, Dict

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

        # Output report data as JSON for external processing
        report_data = {
            'subject': f"Daily Repo Report - {validation_data['repo_info']['name']} ({datetime.now().strftime('%Y-%m-%d')})",
            'html_body': html_report,
            'summary': {
                'repo': validation_data['repo_info']['name'],
                'branch': validation_data['branch_info']['current_branch'],
                'uncommitted_changes': validation_data['repo_status']['uncommitted_changes'],
                'new_commits_24h': validation_data['recent_changes']['main_branch']['new_commits_24h']
            }
        }

        # Output summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Repository: {validation_data['repo_info']['name']}")
        print(f"Current Branch: {validation_data['branch_info']['current_branch']}")
        print(f"Uncommitted Changes: {validation_data['repo_status']['uncommitted_changes']}")
        print(f"New Commits (main, 24h): {validation_data['recent_changes']['main_branch']['new_commits_24h']}")
        print("="*60)
        print("\n✅ Report generated successfully!")
        print("\nTo send this report via Gmail, use:")
        print(f"Subject: {report_data['subject']}")
        print(f"\nHTML Body prepared with {len(html_report)} characters")

        # Save JSON for reference
        report_json_file = f"report_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n📄 Report data saved to: {report_json_file}")

    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
