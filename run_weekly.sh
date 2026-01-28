#!/bin/bash
# Local wrapper to run grant scraper once per week (on Mondays)

SCRIPT_DIR="/Users/dtyrrell/Projects/grant_scraper"
TIMESTAMP_FILE="$SCRIPT_DIR/.last_run_week"
LOG_FILE="$SCRIPT_DIR/grant_scraper.log"

# Get current week number and year (to handle year boundaries)
CURRENT_WEEK=$(date +%Y-W%V)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday

# Only run on Mondays (day 1)
if [ "$DAY_OF_WEEK" != "1" ]; then
    exit 0
fi

# Check if already run this week
if [ -f "$TIMESTAMP_FILE" ]; then
    LAST_RUN=$(cat "$TIMESTAMP_FILE")
    if [ "$LAST_RUN" = "$CURRENT_WEEK" ]; then
        echo "$(date): Already ran this week ($CURRENT_WEEK), skipping." >> "$LOG_FILE"
        exit 0
    fi
fi

echo "$(date): Running grant scraper..." >> "$LOG_FILE"

cd "$SCRIPT_DIR"
/usr/bin/python3 -m src.main --send-email >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "$CURRENT_WEEK" > "$TIMESTAMP_FILE"
    echo "$(date): Completed successfully." >> "$LOG_FILE"
else
    echo "$(date): Failed with exit code $EXIT_CODE" >> "$LOG_FILE"
fi

exit $EXIT_CODE
