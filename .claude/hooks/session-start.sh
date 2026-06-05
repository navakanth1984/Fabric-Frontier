#!/bin/bash
# Run once at the start of a session (call manually or via SessionStart hook).
# Wires git remote to use FABRIC_PAT so every session can push without setup.

REPO="navakanth1984/Fabric-Frontier"

if [ -n "${FABRIC_PAT:-}" ]; then
  git remote set-url origin "https://${FABRIC_PAT}@github.com/${REPO}.git"
  echo "[session-start] Remote wired with FABRIC_PAT."
  git push --dry-run origin HEAD 2>&1 | grep -q "Would delete\|up-to-date\|new branch\| -> " \
    && echo "[session-start] Push access: OK" \
    || echo "[session-start] Push access: BLOCKED — check FABRIC_PAT has Contents: write."
else
  echo "[session-start] WARNING: FABRIC_PAT not set. Pushes will fail."
  echo "  Fix: add FABRIC_PAT=<token> in session environment variables."
  echo "  Token needs: repo=navakanth1984/Fabric-Frontier, permission=Contents: write"
fi
