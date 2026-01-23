"""Main entry point for NIH Grant Scraper."""

import argparse
import sys

from .nih_reporter import fetch_new_awards, format_award_for_display
from .nofo_scraper import fetch_nofos, format_nofo_for_display
from .email_sender import send_digest, build_digest_html, build_plain_text


def run_scraper(send_email: bool = True, verbose: bool = False) -> dict:
    """Run the grant scraper and optionally send email digest."""

    print("Fetching new R01 awards from NIH Reporter...")
    raw_awards = fetch_new_awards()
    awards = [format_award_for_display(a) for a in raw_awards]
    print(f"  Found {len(awards)} matching awards")

    print("Fetching new NOFOs from NIH Guide...")
    raw_nofos = fetch_nofos()
    nofos = [format_nofo_for_display(n) for n in raw_nofos]
    print(f"  Found {len(nofos)} matching funding opportunities")

    if verbose:
        print("\n" + "=" * 50)
        print("TOP AWARDS:")
        for award in awards[:5]:
            print(f"  - {award['title'][:60]}...")
            print(f"    PI: {award['pi_name']}, Score: {award['relevance_score']}")

        print("\nTOP NOFOs:")
        for nofo in nofos[:5]:
            print(f"  - {nofo['title'][:60]}...")
            print(f"    Score: {nofo['relevance_score']}")
        print("=" * 50 + "\n")

    if send_email:
        print("Sending email digest...")
        success = send_digest(awards, nofos)
        if success:
            print("Email sent successfully!")
        else:
            print("Failed to send email.")
            return {"success": False, "awards": len(awards), "nofos": len(nofos)}
    else:
        print("\nEmail sending disabled. Use --send-email to send.")
        # Print plain text summary instead
        print("\n" + build_plain_text(awards, nofos))

    return {"success": True, "awards": len(awards), "nofos": len(nofos)}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NIH Grant Scraper - Weekly digest of R01 awards and NOFOs"
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send the digest via email (requires SENDGRID_API_KEY)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed output"
    )
    parser.add_argument(
        "--html-preview",
        action="store_true",
        help="Output HTML to stdout for preview"
    )

    args = parser.parse_args()

    if args.html_preview:
        raw_awards = fetch_new_awards()
        awards = [format_award_for_display(a) for a in raw_awards]
        raw_nofos = fetch_nofos()
        nofos = [format_nofo_for_display(n) for n in raw_nofos]
        print(build_digest_html(awards, nofos))
        return

    result = run_scraper(send_email=args.send_email, verbose=args.verbose)

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
