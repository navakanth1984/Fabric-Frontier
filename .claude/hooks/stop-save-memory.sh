#!/bin/bash
# Fires on every Claude Code agent stop.
# 1. Logs timestamped entry to today's session file.
# 2. If GITHUB_TOKEN is set, commits any untracked files and pushes.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo ".")"
LOG_DIR="$REPO_ROOT/memory_os/session_memory"
mkdir -p "$LOG_DIR"

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
LOG_FILE="$LOG_DIR/session_${DATE}.md"

# --- 1. Write session log entry ---
if [ ! -f "$LOG_FILE" ]; then
  printf "# Session Log — %s\n\n" "$DATE" > "$LOG_FILE"
fi
printf "## Stop event — %s\n\nAgent stopped.\n\n" "$TIME" >> "$LOG_FILE"

# --- 2. Auto-commit untracked/modified files and push ---
cd "$REPO_ROOT"

# Wire remote if GITHUB_TOKEN is available
if [ -n "${GITHUB_TOKEN:-}" ]; then
  git remote set-url origin "https://${GITHUB_TOKEN}@github.com/navakanth1984/Fabric-Frontier.git"
fi

# Stage any untracked or modified files (excluding .env and secrets)
UNTRACKED=$(git status --porcelain | grep -v '^\?\? \.env' || true)
if [ -n "$UNTRACKED" ]; then
  git add --all -- ':!.env' ':!*.pem' ':!*.key'
  git commit -m "chore(auto): commit untracked files at session stop [$(date +%Y-%m-%dT%H:%M:%S)]" || true
fi

# Push if there are unpushed commits
BRANCH=$(git rev-parse --abbrev-ref HEAD)
UNPUSHED=$(git log "origin/${BRANCH}..HEAD" --oneline 2>/dev/null || true)
if [ -n "$UNPUSHED" ]; then
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    git push -u origin "$BRANCH" && echo "[stop-hook] Pushed to ${BRANCH}." \
      || echo "[stop-hook] Push failed. Check GITHUB_TOKEN has Contents: write scope."
  else
    echo "[stop-hook] WARNING: ${BRANCH} has unpushed commits but GITHUB_TOKEN is not set."
    echo "  Add GITHUB_TOKEN to session env vars to enable auto-push."
  fi
fi
