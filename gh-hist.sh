#!/bin/bash

# Default values
DAYS=7
START_DATE=""
END_DATE=""

# Help message
show_help() {
    cat << EOF
Usage: gh-hist.sh [OPTIONS]

Fetch GitHub activity for the authenticated user.

Options:
  -h          Show this help message
  -d DAYS     Number of days (default: 7)
  -s DATE     Start date (with -d: go forward X days; without -d: to today)
  -e DATE     End date (with -d: go backward X days; default: today)

Examples:
  gh-hist.sh                        # Last 7 days
  gh-hist.sh -d 14                  # Last 14 days
  gh-hist.sh -e 2025-11-01          # 7 days ending Nov 1
  gh-hist.sh -e 2025-11-01 -d 14    # 14 days ending Nov 1
  gh-hist.sh -s 2025-11-01          # Nov 1 to today
  gh-hist.sh -s 2025-11-01 -d 7     # Nov 1 to Nov 8

Note: -s and -e are mutually exclusive.
EOF
    exit 0
}

# Parse arguments
while getopts "hd:s:e:" opt; do
    case $opt in
        h) show_help ;;
        d) DAYS="$OPTARG" ;;
        s) START_DATE="$OPTARG" ;;
        e) END_DATE="$OPTARG" ;;
        *) show_help ;;
    esac
done

# Validate: -s and -e are mutually exclusive
if [[ -n "$START_DATE" && -n "$END_DATE" ]]; then
    echo "Error: -s and -e are mutually exclusive"
    exit 1
fi

# Calculate date range
if [[ -n "$START_DATE" ]]; then
    # Start date provided
    SINCE="$START_DATE"
    if [[ $DAYS -gt 0 ]]; then
        # -d provided: go forward X days
        END=$(date -d "$START_DATE + $DAYS days" +%Y-%m-%d)
    else
        # No -d: go to today
        END=$(date +%Y-%m-%d)
    fi
elif [[ -n "$END_DATE" ]]; then
    # End date provided: go backward
    END="$END_DATE"
    SINCE=$(date -d "$END_DATE - $DAYS days" +%Y-%m-%d)
else
    # Default: last X days from today
    END=$(date +%Y-%m-%d)
    SINCE=$(date -d "$DAYS days ago" +%Y-%m-%d)
fi

# Get username from authenticated session
USERNAME=$(gh api user --jq .login)
if [[ -z "$USERNAME" ]]; then
    echo "Error: Not logged in. Run 'gh auth login' first."
    exit 1
fi

# Create output directory based on date range
SINCE_FMT=$(echo $SINCE | tr -d '-')
END_FMT=$(echo $END | tr -d '-')
OUTPUT_DIR="gh_${SINCE_FMT}_${END_FMT}"
mkdir -p "$OUTPUT_DIR"

echo "Fetching GitHub activity for $USERNAME"
echo "  Range: $SINCE to $END"
echo ""

# Date range for GitHub search
DATE_RANGE="$SINCE..$END"

# Commits
echo "Fetching commits..."
gh search commits --author=$USERNAME --committer-date="$DATE_RANGE" --limit=100 \
  --json repository,sha,commit > "$OUTPUT_DIR/commits.json"

# Issues created
echo "Fetching issues created..."
gh search issues --author=$USERNAME --created="$DATE_RANGE" --limit=100 \
  --json repository,title,state,createdAt,url,body > "$OUTPUT_DIR/issues_created.json"

# Issues commented on
echo "Fetching issues commented on..."
gh search issues --commenter=$USERNAME --updated="$DATE_RANGE" --limit=100 \
  --json repository,title,state,url > "$OUTPUT_DIR/issues_commented.json"

# PRs created
echo "Fetching PRs created..."
gh search prs --author=$USERNAME --created="$DATE_RANGE" --limit=100 \
  --json repository,title,state,createdAt,url,body > "$OUTPUT_DIR/prs_created.json"

# PRs reviewed
echo "Fetching PRs reviewed..."
gh search prs --reviewed-by=$USERNAME --updated="$DATE_RANGE" --limit=100 \
  --json repository,title,state,url > "$OUTPUT_DIR/prs_reviewed.json"

echo ""
echo "Done! Output saved to $OUTPUT_DIR"
echo ""
echo "Summary:"
echo "  Commits: $(jq length "$OUTPUT_DIR/commits.json")"
echo "  Issues created: $(jq length "$OUTPUT_DIR/issues_created.json")"
echo "  Issues commented: $(jq length "$OUTPUT_DIR/issues_commented.json")"
echo "  PRs created: $(jq length "$OUTPUT_DIR/prs_created.json")"
echo "  PRs reviewed: $(jq length "$OUTPUT_DIR/prs_reviewed.json")"
