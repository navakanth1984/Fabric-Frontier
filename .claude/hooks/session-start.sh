#!/bin/bash
# Run once at the start of a session (call manually or via SessionStart hook).
# Wires git remote to use GITHUB_TOKEN so every session can push without setup.

REPO="navakanth1984/Fabric-Frontier"

if [ -n "${GITHUB_TOKEN:-}" ]; then
  git remote set-url origin "https://${GITHUB_TOKEN}@github.com/${REPO}.git"
  echo "[session-start] Remote wired with GITHUB_TOKEN."
  git push --dry-run origin HEAD 2>&1 | grep -q "Would delete\|up-to-date\|new branch\| -> " \
    && echo "[session-start] Push access: OK" \
    || echo "[session-start] Push access: BLOCKED — check GITHUB_TOKEN has Contents: write."
else
  echo "[session-start] WARNING: GITHUB_TOKEN not set. Pushes will fail."
  echo "  Fix: add GITHUB_TOKEN=<token> in session environment variables."
  echo "  Token needs: repo=navakanth1984/Fabric-Frontier, permission=Contents: write"
fi
