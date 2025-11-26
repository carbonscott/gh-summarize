#!/usr/bin/env python3
"""
Transform GitHub activity JSON files into LLM-friendly Hybrid Markdown.

Usage:
    python gh-hist-to-md.py gh_20251125
    python gh-hist-to-md.py gh_20251125 -o custom_output.md
    python gh-hist-to-md.py gh_20251125 --include-body
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_json(filepath):
    """Load JSON file, return empty list if file doesn't exist or is empty."""
    try:
        with open(filepath) as f:
            data = json.load(f)
            return data if data else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def parse_date(iso_string):
    """Parse ISO date string to datetime, return None on failure."""
    if not iso_string:
        return None
    try:
        # Handle various ISO formats
        iso_string = iso_string.replace('Z', '+00:00')
        if '+' in iso_string or '-' in iso_string[10:]:
            return datetime.fromisoformat(iso_string)
        return datetime.fromisoformat(iso_string)
    except ValueError:
        return None


def format_date(dt):
    """Format datetime as 'Mon DD'."""
    if not dt:
        return ""
    return dt.strftime("%b %d")


def get_first_line(text):
    """Get first line of text, truncated if needed."""
    if not text:
        return ""
    first_line = text.split('\n')[0].strip()
    if len(first_line) > 80:
        return first_line[:77] + "..."
    return first_line


def process_commits(data):
    """Group commits by repository."""
    grouped = defaultdict(list)
    for item in data:
        repo = item.get('repository', {}).get('name', 'unknown')
        commit = item.get('commit', {})
        author = commit.get('author', {})
        date = parse_date(author.get('date'))
        message = get_first_line(commit.get('message', ''))
        grouped[repo].append({
            'date': date,
            'message': message,
        })
    # Sort each repo's commits by date (newest first)
    for repo in grouped:
        grouped[repo].sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    return grouped


def process_issues(data):
    """Group issues by repository."""
    grouped = defaultdict(list)
    for item in data:
        repo = item.get('repository', {}).get('nameWithOwner',
               item.get('repository', {}).get('name', 'unknown'))
        date = parse_date(item.get('createdAt'))
        grouped[repo].append({
            'title': item.get('title', ''),
            'state': item.get('state', '').lower(),
            'date': date,
            'url': item.get('url', ''),
            'body': item.get('body', ''),
        })
    # Sort by date (newest first)
    for repo in grouped:
        grouped[repo].sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    return grouped


def process_prs(data):
    """Group PRs by repository."""
    grouped = defaultdict(list)
    for item in data:
        repo = item.get('repository', {}).get('nameWithOwner',
               item.get('repository', {}).get('name', 'unknown'))
        date = parse_date(item.get('createdAt'))
        grouped[repo].append({
            'title': item.get('title', ''),
            'state': item.get('state', '').lower(),
            'date': date,
            'url': item.get('url', ''),
            'merged': item.get('state', '').lower() == 'merged',
            'body': item.get('body', ''),
        })
    for repo in grouped:
        grouped[repo].sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    return grouped


def format_body(body, indent="  "):
    """Format body text as indented blockquote lines."""
    if not body or not body.strip():
        return []
    lines = []
    for line in body.strip().split('\n'):
        lines.append(f"{indent}> {line}")
    return lines


def generate_markdown(commits, issues_created, issues_commented, prs_created, prs_reviewed, dir_name, include_body=False):
    """Generate the hybrid markdown output."""
    lines = []

    # Calculate date range from all data
    all_dates = []
    for repo_items in commits.values():
        all_dates.extend([i['date'] for i in repo_items if i['date']])
    for repo_items in issues_created.values():
        all_dates.extend([i['date'] for i in repo_items if i['date']])

    if all_dates:
        min_date = min(all_dates).strftime("%Y-%m-%d")
        max_date = max(all_dates).strftime("%Y-%m-%d")
        period = f"{min_date} to {max_date}"
    else:
        period = "unknown"

    # Count totals
    total_commits = sum(len(items) for items in commits.values())
    total_issues_created = sum(len(items) for items in issues_created.values())
    total_issues_commented = sum(len(items) for items in issues_commented.values())
    total_prs_created = sum(len(items) for items in prs_created.values())
    total_prs_reviewed = sum(len(items) for items in prs_reviewed.values())

    # YAML frontmatter
    lines.append("---")
    lines.append(f"period: {period}")
    lines.append(f"source: {dir_name}")
    lines.append(f"commits: {total_commits}")
    lines.append(f"issues_created: {total_issues_created}")
    lines.append(f"issues_commented: {total_issues_commented}")
    lines.append(f"prs_created: {total_prs_created}")
    lines.append(f"prs_reviewed: {total_prs_reviewed}")
    lines.append("---")
    lines.append("")
    lines.append("# Weekly GitHub Activity")
    lines.append("")

    # Commits section
    lines.append(f"## Commits ({total_commits})")
    lines.append("")
    if commits:
        for repo in sorted(commits.keys()):
            lines.append(f"### {repo}")
            for item in commits[repo]:
                date_str = format_date(item['date'])
                date_part = f" ({date_str})" if date_str else ""
                lines.append(f"- {item['message']}{date_part}")
            lines.append("")
    else:
        lines.append("None")
        lines.append("")

    # Issues Created section
    lines.append(f"## Issues Created ({total_issues_created})")
    lines.append("")
    if issues_created:
        for repo in sorted(issues_created.keys()):
            lines.append(f"### {repo}")
            for item in issues_created[repo]:
                date_str = format_date(item['date'])
                date_part = f" ({date_str})" if date_str else ""
                state = f" [{item['state']}]" if item['state'] else ""
                lines.append(f"- {item['title']}{date_part}{state}")
                if include_body:
                    lines.extend(format_body(item.get('body', '')))
            lines.append("")
    else:
        lines.append("None")
        lines.append("")

    # Issues Commented section
    lines.append(f"## Issues Commented ({total_issues_commented})")
    lines.append("")
    if issues_commented:
        for repo in sorted(issues_commented.keys()):
            lines.append(f"### {repo}")
            for item in issues_commented[repo]:
                state = f" [{item['state']}]" if item['state'] else ""
                lines.append(f"- {item['title']}{state}")
            lines.append("")
    else:
        lines.append("None")
        lines.append("")

    # PRs Created section
    lines.append(f"## PRs Created ({total_prs_created})")
    lines.append("")
    if prs_created:
        for repo in sorted(prs_created.keys()):
            lines.append(f"### {repo}")
            for item in prs_created[repo]:
                date_str = format_date(item['date'])
                date_part = f" ({date_str})" if date_str else ""
                if item['merged']:
                    state = " [merged]"
                else:
                    state = f" [{item['state']}]" if item['state'] else ""
                lines.append(f"- {item['title']}{date_part}{state}")
                if include_body:
                    lines.extend(format_body(item.get('body', '')))
            lines.append("")
    else:
        lines.append("None")
        lines.append("")

    # PRs Reviewed section
    lines.append(f"## PRs Reviewed ({total_prs_reviewed})")
    lines.append("")
    if prs_reviewed:
        for repo in sorted(prs_reviewed.keys()):
            lines.append(f"### {repo}")
            for item in prs_reviewed[repo]:
                state = f" [{item['state']}]" if item['state'] else ""
                lines.append(f"- {item['title']}{state}")
            lines.append("")
    else:
        lines.append("None")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Transform GitHub activity JSON to Hybrid Markdown"
    )
    parser.add_argument("directory", help="Directory containing JSON files (e.g., gh_20251125)")
    parser.add_argument("-o", "--output", help="Output file (default: {directory}/summary.md)")
    parser.add_argument("--include-body", action="store_true", help="Include issue/PR body text")
    args = parser.parse_args()

    dir_path = Path(args.directory)
    if not dir_path.is_dir():
        print(f"Error: {args.directory} is not a directory")
        return 1

    # Load all JSON files
    commits_data = load_json(dir_path / "commits.json")
    issues_created_data = load_json(dir_path / "issues_created.json")
    issues_commented_data = load_json(dir_path / "issues_commented.json")
    prs_created_data = load_json(dir_path / "prs_created.json")
    prs_reviewed_data = load_json(dir_path / "prs_reviewed.json")

    # Process data
    commits = process_commits(commits_data)
    issues_created = process_issues(issues_created_data)
    issues_commented = process_issues(issues_commented_data)
    prs_created = process_prs(prs_created_data)
    prs_reviewed = process_prs(prs_reviewed_data)

    # Generate markdown
    markdown = generate_markdown(
        commits, issues_created, issues_commented,
        prs_created, prs_reviewed, dir_path.name,
        include_body=args.include_body
    )

    # Write output
    output_path = Path(args.output) if args.output else dir_path / "summary.md"
    output_path.write_text(markdown)
    print(f"Generated: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
