#!/bin/bash
# Sponsor Bot – Thiago Berenstein
# Runs via cron daily at 9:00 AM Argentina time
# Usage: ./run.sh [--dry-run]

set -e
cd "$(dirname "$0")"

LOG_FILE="data/run_$(date +%Y-%m-%d).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting sponsor bot..." | tee -a "$LOG_FILE"

# Run claude CLI with the sponsor bot prompt
claude --print \
  --allowedTools "mcp__Gmail__search_threads,mcp__Gmail__get_thread,mcp__Gmail__create_draft,mcp__Gmail__label_message,mcp__Gmail__label_thread,mcp__Gmail__list_labels,mcp__Google_Calendar__create_event,WebSearch,Read,Write" \
  "run sponsor bot" \
  2>&1 | tee -a "$LOG_FILE"

echo "[$TIMESTAMP] Done." | tee -a "$LOG_FILE"
