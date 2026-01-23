# NIH Grant Scraper

A simple tool to stay informed on NIH grants relevant to my research interests (aging, mitochondria, immunology, cardiovascular, neuroinflammation).

## What It Does

Every Monday at 6:00am CST, this tool automatically:

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

## Automation

Runs weekly via GitHub Actions. Secrets (`RESEND_API_KEY`, `EMAIL_SENDER`, `EMAIL_RECIPIENT`) are configured in the repository settings.
