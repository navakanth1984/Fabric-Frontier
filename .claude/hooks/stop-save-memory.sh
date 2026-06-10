#!/bin/bash
# Fires on every Claude Code agent stop.
# Writes session log, commits ALL untracked/modified files, and pushes.
# Order matters: commit must happen before the system hook checks git state.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo ".")"
cd "$REPO_ROOT"

LOG_DIR="$REPO_ROOT/memory_os/session_memory"
mkdir -p "$LOG_DIR"

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
LOG_FILE="$LOG_DIR/session_${DATE}.md"

# Write session log entry
if [ ! -f "$LOG_FILE" ]; then
  printf "# Session Log — %s\n\n" "$DATE" > "$LOG_FILE"
fi
printf "## Stop event — %s\n\nAgent stopped.\n\n" "$TIME" >> "$LOG_FILE"

# Wire remote if GITHUB_TOKEN is available
if [ -n "${GITHUB_TOKEN:-}" ]; then
  git remote set-url origin "https://${GITHUB_TOKEN}@github.com/navakanth1984/Fabric-Frontier.git"
fi

# Commit everything untracked/modified (excluding secrets)
if [ -n "$(git status --porcelain)" ]; then
  git add --all -- ':!.env' ':!*.pem' ':!*.key'
  git commit -m "chore(session): auto-commit at stop [${DATE}T${TIME}]" || true
fi

# Push unpushed commits
BRANCH=$(git rev-parse --abbrev-ref HEAD)
UNPUSHED=$(git rev-list "origin/${BRANCH}..HEAD" --count 2>/dev/null || echo "0")
if [ "$UNPUSHED" -gt 0 ]; then
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    git push -u origin "$BRANCH" \
      && echo "[stop-hook] Pushed $UNPUSHED commit(s) to ${BRANCH}." \
      || echo "[stop-hook] Push failed — check GITHUB_TOKEN has Contents: write scope."
  else
    echo "[stop-hook] WARNING: $UNPUSHED unpushed commit(s) but GITHUB_TOKEN not set."
  fi
fi
