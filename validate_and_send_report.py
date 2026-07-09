#!/usr/bin/env python3
"""
Repository validation and reporting via Gmail MCP tools.
This script validates the repository daily and sends reports to Gmail.
Uses Gmail MCP server for sending emails (no SMTP credentials needed).
"""

import subprocess
import json
from datetime import datetime, timedelta
from typing import List, Dict
import sys

def run_command(cmd: str) -> str:
    """Execute shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/home/user/x-devops")
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

    # Fetch latest changes
    run_command("git fetch origin")

    # Check git status
    status = run_command("git status --short")
    uncommitted = [line for line in status.split('\n') if line.strip()] if status else []
    validation_report['repo_status']['uncommitted_changes'] = len(uncommitted)
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

    # Get current branch info vs main
    current_branch_commits = get_git_log(days=7, branch=current_branch) if current_branch != "main" else []
    validation_report['recent_changes']['current_branch'] = {
        'new_commits_7d': len(current_branch_commits),
        'commits': current_branch_commits[:10]  # Limit to 10 for readability
    }

    # Repository info
    repo_name = run_command("git config --get remote.origin.url").split('/')[-1].replace('.git', '')
    remote_url = run_command("git config --get remote.origin.url")
    validation_report['repo_info'] = {
        'name': repo_name,
        'remote_url': remote_url
    }

    # Check uncommitted changes in detail
    if uncommitted:
        validation_report['repo_status']['changes_detail'] = uncommitted[:20]  # Limit to 20 lines

    return validation_report

def format_html_report(validation_data: Dict) -> str:
    """Format validation report as HTML email."""
    repo_name = validation_data['repo_info']['name']
    timestamp = validation_data['timestamp']
    branch = validation_data['branch_info']['current_branch']
    uncommitted = validation_data['repo_status']['uncommitted_changes']
    status = validation_data['repo_status']['status_output']
    new_commits = validation_data['recent_changes']['main_branch']['new_commits_24h']

    html = f"""<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5; margin: 0; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #0066cc; padding-bottom: 15px; margin-bottom: 20px; }}
        h2 {{ color: #0066cc; margin-top: 25px; margin-bottom: 12px; font-size: 18px; }}
        .summary-box {{ background-color: #f0f7ff; padding: 15px; border-left: 4px solid #0066cc; margin: 15px 0; border-radius: 4px; }}
        .status-clean {{ background-color: #d4edda; padding: 12px; border-radius: 4px; border-left: 4px solid #28a745; }}
        .status-warning {{ background-color: #fff3cd; padding: 12px; border-radius: 4px; border-left: 4px solid #ffc107; }}
        .status-changes {{ background-color: #cfe2ff; padding: 12px; border-radius: 4px; border-left: 4px solid #0066cc; }}
        .timestamp {{ color: #666; font-size: 12px; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
        th {{ background-color: #0066cc; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background-color: #f9f9f9; }}
        tr:last-child td {{ border-bottom: none; }}
        code {{ background-color: #f4f4f4; padding: 3px 6px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 13px; }}
        .stat-value {{ font-weight: bold; color: #0066cc; font-size: 18px; }}
        .footer {{ color: #999; font-size: 11px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Repository Validation Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>

        <div class="summary-box">
            <strong>Repository:</strong> {repo_name}<br>
            <strong>Branch:</strong> <code>{branch}</code><br>
            <strong>Uncommitted Changes:</strong> <span class="stat-value">{uncommitted}</span>
        </div>

        <h2>Repository Status</h2>
"""

    if uncommitted == 0:
        html += '<div class="status-clean">✅ <strong>Clean working directory</strong> - No uncommitted changes</div>'
    else:
        html += f'<div class="status-warning">⚠️ <strong>{uncommitted} uncommitted changes</strong> detected</div>'
        if 'changes_detail' in validation_data['repo_status']:
            html += '<table><tr><th>File Status</th></tr>'
            for change in validation_data['repo_status']['changes_detail']:
                html += f'<tr><td><code>{change}</code></td></tr>'
            html += '</table>'

    html += """
        <h2>Changes from Main Branch (Last 24 Hours)</h2>
        <div class="summary-box">
            <strong>Total New Commits:</strong> <span class="stat-value">"""
    html += str(new_commits)
    html += """</span>
        </div>
"""

    commits = validation_data['recent_changes']['main_branch']['commits']
    if commits:
        html += """<table>
            <tr>
                <th>Commit Hash</th>
                <th>Author</th>
                <th>Date</th>
                <th>Message</th>
            </tr>
"""
        for commit in commits[:10]:  # Show last 10 commits
            date_str = commit['date'][:10]
            html += f"""<tr>
                <td><code>{commit['hash']}</code></td>
                <td>{commit['author']}</td>
                <td>{date_str}</td>
                <td>{commit['message']}</td>
            </tr>
"""
        html += '</table>'
    else:
        html += '<p><em>No new commits in the last 24 hours on main branch.</em></p>'

    # Current branch info
    current_branch = validation_data['branch_info']['current_branch']
    if current_branch != "main":
        current_commits = validation_data['recent_changes']['current_branch']['commits']
        current_count = validation_data['recent_changes']['current_branch']['new_commits_7d']
        html += f"""
        <h2>Changes from Current Branch (Last 7 Days)</h2>
        <div class="summary-box">
            <strong>Branch:</strong> <code>{current_branch}</code><br>
            <strong>Total Commits:</strong> <span class="stat-value">{current_count}</span>
        </div>
"""
        if current_commits:
            html += """<table>
                <tr>
                    <th>Hash</th>
                    <th>Author</th>
                    <th>Date</th>
                    <th>Message</th>
                </tr>
"""
            for commit in current_commits:
                date_str = commit['date'][:10]
                html += f"""<tr>
                    <td><code>{commit['hash']}</code></td>
                    <td>{commit['author']}</td>
                    <td>{date_str}</td>
                    <td>{commit['message']}</td>
                </tr>
"""
            html += '</table>'

    html += f"""
        <div class="footer">
            <p>This is an automated daily repository validation report. Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} UTC.</p>
            <p>Repository: {repo_name} | Remote: {validation_data['repo_info']['remote_url']}</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def save_report_data(validation_data: Dict, html_report: str) -> Dict:
    """Save report data and return formatted report info."""
    report_info = {
        'subject': f"Daily Repository Report - {validation_data['repo_info']['name']} ({datetime.now().strftime('%Y-%m-%d')})",
        'html_body': html_report,
        'text_summary': f"""
Repository: {validation_data['repo_info']['name']}
Branch: {validation_data['branch_info']['current_branch']}
Uncommitted Changes: {validation_data['repo_status']['uncommitted_changes']}
New Commits (main, 24h): {validation_data['recent_changes']['main_branch']['new_commits_24h']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """.strip()
    }
    return report_info

def main():
    """Main execution function."""
    print("🔍 Starting repository validation...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    try:
        # Validate repository
        print("📊 Analyzing repository...")
        validation_data = validate_repository()

        # Format report
        html_report = format_html_report(validation_data)
        report_info = save_report_data(validation_data, html_report)

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
        print(f"📧 Subject: {report_info['subject']}")
        print(f"📄 Report size: {len(html_report)} characters")
        print(f"\n💾 To send this via Gmail, use the Gmail MCP tools with:")
        print(f"   Recipient: sathishkr.cs@gmail.com")
        print(f"   Subject: {report_info['subject']}")

        # Save JSON for debugging
        report_json_file = f"/tmp/claude-0/-home-user-x-devops/555badbd-c322-54fc-b4ca-af19b37f38ac/scratchpad/report_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_json_file, 'w') as f:
                json.dump({
                    'validation': validation_data,
                    'report_info': report_info
                }, f, indent=2)
            print(f"📋 Report data saved to: {report_json_file}")
        except Exception as e:
            print(f"⚠️  Could not save report data: {e}")

        return True

    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
