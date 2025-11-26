# GitHub Activity Tracker

Scripts to fetch and summarize your GitHub activity from the past 7 days.

## Prerequisites

### Install GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# HPC (via conda)
conda install -c conda-forge gh

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
./gh-hist.sh                        # Last 7 days
./gh-hist.sh -h                     # Show help
./gh-hist.sh -d 14                  # Last 14 days
./gh-hist.sh -e 2025-11-01          # 7 days ending Nov 1
./gh-hist.sh -e 2025-11-01 -d 14    # 14 days ending Nov 1
./gh-hist.sh -s 2025-11-01          # Nov 1 to today
./gh-hist.sh -s 2025-11-01 -d 7     # Nov 1 to Nov 8
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

## Notes

- Username is auto-detected from your `gh auth login` session
- `-s` and `-e` are mutually exclusive
