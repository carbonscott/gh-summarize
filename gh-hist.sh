#!/bin/bash

USERNAME="carbonscott"
SINCE=$(date -d "7 days ago" +%Y-%m-%d)
OUTPUT_DIR="gh_$(date +%Y%m%d)"

mkdir -p "$OUTPUT_DIR"

echo "Fetching GitHub activity for $USERNAME since $SINCE..."

# Commits
echo "Fetching commits..."
gh search commits --author=$USERNAME --committer-date=">=$SINCE" --limit=100 \
  --json repository,sha,commit > "$OUTPUT_DIR/commits.json"

# Issues created
echo "Fetching issues created..."
gh search issues --author=$USERNAME --created=">=$SINCE" --limit=100 \
  --json repository,title,state,createdAt,url,body > "$OUTPUT_DIR/issues_created.json"

# Issues commented on
echo "Fetching issues commented on..."
gh search issues --commenter=$USERNAME --updated=">=$SINCE" --limit=100 \
  --json repository,title,state,url > "$OUTPUT_DIR/issues_commented.json"

# PRs created
echo "Fetching PRs created..."
gh search prs --author=$USERNAME --created=">=$SINCE" --limit=100 \
  --json repository,title,state,createdAt,mergedAt,url,body > "$OUTPUT_DIR/prs_created.json"

# PRs reviewed
echo "Fetching PRs reviewed..."
gh search prs --reviewed-by=$USERNAME --updated=">=$SINCE" --limit=100 \
  --json repository,title,state,url > "$OUTPUT_DIR/prs_reviewed.json"

echo "Done! Output saved to $OUTPUT_DIR"
echo ""
echo "Summary:"
echo "  Commits: $(jq length "$OUTPUT_DIR/commits.json")"
echo "  Issues created: $(jq length "$OUTPUT_DIR/issues_created.json")"
echo "  Issues commented: $(jq length "$OUTPUT_DIR/issues_commented.json")"
echo "  PRs created: $(jq length "$OUTPUT_DIR/prs_created.json")"
echo "  PRs reviewed: $(jq length "$OUTPUT_DIR/prs_reviewed.json")"
