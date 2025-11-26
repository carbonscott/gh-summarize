# GitHub Activity Tracker

Scripts to fetch and summarize your GitHub activity from the past 7 days.

## Prerequisites

### Install GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Or download from: https://cli.github.com/
```

### Authenticate

```bash
gh auth login
```

Follow the prompts to authenticate with your GitHub account.

## Usage

### 1. Fetch GitHub Activity

```bash
./gh-hist.sh
```

This creates a directory `gh_YYYYMMDD/` containing:
- `commits.json` - Your commits
- `issues_created.json` - Issues you created
- `issues_commented.json` - Issues you commented on
- `prs_created.json` - Pull requests you created
- `prs_reviewed.json` - Pull requests you reviewed

### 2. Generate Markdown Summary

```bash
# Basic summary
python gh-hist-to-md.py gh_20251125

# Include issue/PR body text
python gh-hist-to-md.py gh_20251125 --include-body

# Custom output file
python gh-hist-to-md.py gh_20251125 -o my_summary.md
```

Output is a hybrid markdown file with YAML frontmatter, suitable for LLM consumption.

## Configuration

Edit `gh-hist.sh` to change:
- `USERNAME` - Your GitHub username (default: carbonscott)
- `SINCE` - Date range (default: 7 days ago)
