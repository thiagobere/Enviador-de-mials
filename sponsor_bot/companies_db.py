"""Manages the local database of contacted companies."""

import json
import os
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "companies.json"


def load_db() -> dict:
    if not DB_PATH.exists():
        return {"contacted": [], "pending_response": [], "blacklist": [], "last_updated": str(date.today())}
    with open(DB_PATH) as f:
        return json.load(f)


def save_db(db: dict):
    db["last_updated"] = str(date.today())
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def get_contacted_emails(db: dict) -> set[str]:
    return {c["email"].lower() for c in db["contacted"]}


def get_contacted_domains(db: dict) -> set[str]:
    domains = set()
    for c in db["contacted"]:
        email = c["email"].lower()
        if "@" in email:
            domains.add(email.split("@")[1])
    return domains


def get_blacklisted_domains(db: dict) -> set[str]:
    return {b.lower() for b in db.get("blacklist", [])}


def is_already_contacted(db: dict, email: str, company: str) -> bool:
    email_lower = email.lower()
    contacted_emails = get_contacted_emails(db)
    contacted_domains = get_contacted_domains(db)
    if email_lower in contacted_emails:
        return True
    if "@" in email_lower:
        domain = email_lower.split("@")[1]
        if domain in contacted_domains:
            return True
    company_lower = company.lower()
    for c in db["contacted"]:
        if c["company"].lower() == company_lower:
            return True
    return False


def add_contacted(db: dict, company: str, email: str, category: str, thread_id: str = ""):
    db["contacted"].append({
        "company": company,
        "email": email,
        "date": str(date.today()),
        "status": "sent",
        "category": category,
        "thread_id": thread_id,
    })


def update_status(db: dict, email: str, status: str, notes: str = ""):
    for c in db["contacted"]:
        if c["email"].lower() == email.lower():
            c["status"] = status
            if notes:
                c["notes"] = notes
            break


def add_to_pending(db: dict, thread_id: str, company: str, email: str, reply_snippet: str):
    for p in db["pending_response"]:
        if p["thread_id"] == thread_id:
            return
    db["pending_response"].append({
        "thread_id": thread_id,
        "company": company,
        "email": email,
        "reply_snippet": reply_snippet,
        "date": str(date.today()),
    })


def remove_from_pending(db: dict, thread_id: str):
    db["pending_response"] = [p for p in db["pending_response"] if p["thread_id"] != thread_id]


def get_todays_sent_count(db: dict) -> int:
    today = str(date.today())
    return sum(1 for c in db["contacted"] if c.get("date") == today)
