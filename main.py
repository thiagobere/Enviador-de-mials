#!/usr/bin/env python3
"""
Sponsor Bot – Thiago Berenstein Karting Pilot
============================================================
Modes:
  --outreach       Find 100 new companies and send sponsorship emails
  --reply          Check for replies on tagged threads and auto-respond
  --all            Run both outreach and reply (default when no flag given)
  --dry-run        Print actions without sending emails
"""

import argparse
import sys
from datetime import date

from sponsor_bot.companies_db import (
    load_db, save_db, add_contacted, get_todays_sent_count
)
from sponsor_bot.company_finder import find_new_companies
from sponsor_bot.email_templates import get_subject, get_outreach_email_html
from sponsor_bot.gmail_client import get_service, send_email, add_label_to_thread
from sponsor_bot.reply_handler import process_bot_replies
from sponsor_bot.config import BOT_LABEL_ID, COMPANIES_PER_DAY


def run_outreach(dry_run: bool = False):
    print(f"\n{'='*50}")
    print(f"[OUTREACH] Starting daily sponsor outreach – {date.today()}")
    print(f"{'='*50}")

    db = load_db()
    already_sent_today = get_todays_sent_count(db)
    remaining = COMPANIES_PER_DAY - already_sent_today

    if remaining <= 0:
        print(f"[INFO] Already sent {already_sent_today} emails today. Skipping outreach.")
        return

    print(f"[INFO] Finding up to {remaining} new companies...")
    companies = find_new_companies(db, target=remaining)
    print(f"[INFO] Found {len(companies)} new candidates.")

    if not companies:
        print("[WARN] No new companies found. Try again later.")
        return

    service = None if dry_run else get_service()
    sent_count = 0

    for company_data in companies:
        company = company_data["company"]
        email = company_data["email"]
        language = company_data.get("language", "en")
        category = company_data.get("category", "general")

        subject = get_subject(company)
        html_body = get_outreach_email_html(company, language=language)

        if dry_run:
            print(f"  [DRY-RUN] Would send to: {email} | {company}")
            add_contacted(db, company, email, category, thread_id="dry-run")
            sent_count += 1
            continue

        try:
            sent = send_email(
                service=service,
                to=email,
                subject=subject,
                html_body=html_body,
                label_ids=[BOT_LABEL_ID],
            )
            thread_id = sent.get("threadId", "")
            add_contacted(db, company, email, category, thread_id=thread_id)
            sent_count += 1
            print(f"  [SENT] {company} → {email} (thread: {thread_id})")
        except Exception as e:
            print(f"  [ERROR] Failed to send to {email}: {e}")

    save_db(db)
    print(f"\n[OUTREACH] Done. Sent {sent_count} emails today.")


def run_reply_handler(dry_run: bool = False):
    print(f"\n{'='*50}")
    print(f"[REPLIES] Checking for sponsor replies – {date.today()}")
    print(f"{'='*50}")

    if dry_run:
        print("[DRY-RUN] Skipping reply handler in dry-run mode.")
        return

    db = load_db()
    service = get_service()

    actions = process_bot_replies(service, db)
    save_db(db)

    if not actions:
        print("[INFO] No unread replies to process.")
    else:
        print(f"\n[REPLIES] Processed {len(actions)} replies:")
        for a in actions:
            cal = f" | 📅 {a['calendar_link']}" if a.get("calendar_link") else ""
            print(f"  ✓ {a['company']} ({a['contact']}) → {a['reply_type']}{cal}")


def main():
    parser = argparse.ArgumentParser(description="Sponsor Bot for Thiago Berenstein")
    parser.add_argument("--outreach", action="store_true", help="Run daily outreach only")
    parser.add_argument("--reply", action="store_true", help="Check and respond to replies only")
    parser.add_argument("--all", dest="run_all", action="store_true", help="Run both (default)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without sending")
    args = parser.parse_args()

    run_all = args.run_all or (not args.outreach and not args.reply)

    if args.outreach or run_all:
        run_outreach(dry_run=args.dry_run)

    if args.reply or run_all:
        run_reply_handler(dry_run=args.dry_run)

    print("\n[BOT] Finished.")


if __name__ == "__main__":
    main()
