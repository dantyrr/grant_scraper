# NIH Grant Scraper

A simple tool to stay informed on NIH grants relevant to my research interests (aging, mitochondria, immunology, cardiovascular, neuroinflammation).

## What It Does

Every Monday, this tool automatically:

1. **Scrapes new R01 awards** from the NIH Reporter API - grants funded in the past week that match my keywords
2. **Scrapes new funding opportunities (NOFOs)** from the NIH Guide RSS feed
3. **Compiles a digest** ranked by relevance to my research areas
4. **Emails the digest** to my inbox

## How It Works

| Package | Purpose |
|---------|---------|
| `requests` | Queries the NIH Reporter API for newly funded R01 grants |
| `feedparser` | Parses the NIH Guide RSS feed for funding opportunities |
| `resend` | Sends the weekly digest email |
| `python-dotenv` | Loads configuration from environment variables |

## Project Structure

```
src/
├── config.py        # Keywords and settings
├── nih_reporter.py  # NIH Reporter API client
├── nofo_scraper.py  # NIH Guide RSS parser
├── email_sender.py  # Email formatting and delivery
└── main.py          # Entry point
```

## Local Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Test without sending email
python -m src.main --verbose

# Send digest
python -m src.main --send-email
```

## Automated Weekly Runs (macOS only)

This project uses macOS launchd for scheduling rather than GitHub Actions or cron. This approach was chosen because most Mac users close their laptop lid rather than shutting down or logging out.

### Why launchd with StartInterval?

- `RunAtLoad` alone only triggers on login, not when waking from sleep
- Since closing the lid puts the Mac to sleep (not logout), `RunAtLoad` wouldn't fire on a typical Monday morning routine of opening the laptop
- `StartInterval` checks periodically (every hour), and the wrapper script ensures it only actually runs once per week (on Mondays)
- This means the digest runs within an hour of waking your Mac on Monday, regardless of whether it was a fresh login, restart, or wake from sleep

### Setup

1. Copy the wrapper script to LaunchAgents:
   ```bash
   cp run_weekly.sh ~/Library/LaunchAgents/grant_scraper_wrapper.sh
   chmod +x ~/Library/LaunchAgents/grant_scraper_wrapper.sh
   ```

2. Update the `SCRIPT_DIR` path in the wrapper script to match your installation location.

3. Create the launchd plist at `~/Library/LaunchAgents/com.dantyrr.grantscraper.plist`:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.dantyrr.grantscraper</string>

       <key>ProgramArguments</key>
       <array>
           <string>/bin/bash</string>
           <string>/Users/YOUR_USERNAME/Library/LaunchAgents/grant_scraper_wrapper.sh</string>
       </array>

       <key>RunAtLoad</key>
       <true/>

       <key>StartInterval</key>
       <integer>3600</integer>

       <key>EnvironmentVariables</key>
       <dict>
           <key>PATH</key>
           <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
       </dict>

       <key>StandardOutPath</key>
       <string>/Users/YOUR_USERNAME/Projects/grant_scraper/launchd_out.log</string>

       <key>StandardErrorPath</key>
       <string>/Users/YOUR_USERNAME/Projects/grant_scraper/launchd_err.log</string>
   </dict>
   </plist>
   ```

4. Load the launch agent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.dantyrr.grantscraper.plist
   ```

### How It Works

1. launchd triggers the wrapper script on login (`RunAtLoad`) and every hour (`StartInterval`)
2. The wrapper first checks if today is Monday - if not, it exits immediately
3. If it's Monday, the wrapper checks `.last_run_week` to see if it already ran this week
4. If already ran this week, it exits immediately (no duplicate emails)
5. If not, it runs the scraper, sends the digest, and updates `.last_run_week`

This means you get your weekly digest within an hour of first opening your Mac on Monday morning.

### Managing the Launch Agent

```bash
# Check status
launchctl list | grep grantscraper

# Reload after config changes
launchctl unload ~/Library/LaunchAgents/com.dantyrr.grantscraper.plist
launchctl load ~/Library/LaunchAgents/com.dantyrr.grantscraper.plist

# View logs
tail -f /path/to/grant_scraper/grant_scraper.log
```

## Logs

- `grant_scraper.log` - Main application log with run timestamps and results
- `launchd_out.log` - stdout from launchd (usually empty)
- `launchd_err.log` - stderr from launchd (warnings, errors)
- `.last_run_week` - Tracks the last successful run week (format: YYYY-WWW)
