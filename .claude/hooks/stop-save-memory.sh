#!/bin/bash
# Fires on every Claude Code agent stop — appends a timestamped entry to today's session log.

LOG_DIR="$(dirname "$0")/../../memory_os/session_memory"
mkdir -p "$LOG_DIR"

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
LOG_FILE="$LOG_DIR/session_${DATE}.md"

if [ ! -f "$LOG_FILE" ]; then
  echo "# Session Log — $DATE" > "$LOG_FILE"
  echo "" >> "$LOG_FILE"
fi

echo "## Stop event — $TIME" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Agent stopped. Review \`memory_os/\` for context." >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
