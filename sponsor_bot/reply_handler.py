"""Handles auto-replies to sponsor responses using Claude API."""

import re
from datetime import date, timedelta
import anthropic

from sponsor_bot.config import (
    PILOT_NAME, PILOT_EMAIL, BOT_LABEL_ID,
    DEFAULT_MEETING_DURATION_MINUTES, DEFAULT_MEETING_HOUR, TIMEZONE
)
from sponsor_bot.gmail_client import (
    get_thread_messages, get_message_body, get_header,
    send_email, mark_message_read, add_label_to_thread
)
from sponsor_bot.calendar_client import create_meeting_event
from sponsor_bot.companies_db import update_status, remove_from_pending


_CLAUDE_CLIENT = None


def _get_claude():
    global _CLAUDE_CLIENT
    if _CLAUDE_CLIENT is None:
        _CLAUDE_CLIENT = anthropic.Anthropic()
    return _CLAUDE_CLIENT


# Keywords that suggest the company wants to meet / talk
_MEETING_SIGNALS = [
    "call", "meeting", "zoom", "google meet", "teams", "schedule",
    "disponible", "llamada", "reunion", "reunión", "videollamada",
    "hablamos", "conversemos", "discutir", "discuss", "chat",
    "interested", "interesado", "interesada", "talk",
]

_DECLINE_SIGNALS = [
    "not at this time", "unfortunately", "unable to", "don't have",
    "no podemos", "no estamos", "no tenemos", "lamentablemente",
    "not currently", "not interested", "pass", "no longer",
    "feel free to reach out again", "vuelve a contactarnos",
    "not set up", "no plans",
]


def _classify_reply(body: str) -> str:
    """Returns: 'meeting', 'interested', 'declined', 'neutral'"""
    body_lower = body.lower()
    if any(s in body_lower for s in _MEETING_SIGNALS):
        return "meeting"
    if any(s in body_lower for s in _DECLINE_SIGNALS):
        return "declined"
    # Check for interest indicators
    if any(w in body_lower for w in ["interested", "love to", "would like", "interesado", "me gustaría"]):
        return "interested"
    return "neutral"


def _generate_reply(
    company: str,
    their_email_body: str,
    reply_type: str,
    language: str = "en",
) -> str:
    """Use Claude to generate a tailored reply."""
    system = (
        f"You are {PILOT_NAME}, a karting pilot, engineering student, and content creator from Argentina. "
        f"You are writing professional sponsorship negotiation emails. "
        f"Be warm, enthusiastic, professional, and concise. "
        f"Your goal is to close a sponsorship deal or set up a meeting. "
        f"Reply in {'Spanish' if language == 'es' else 'English'}. "
        f"Output ONLY the email body (no subject, no metadata), in plain text (no HTML)."
    )

    if reply_type == "meeting":
        task = (
            f"The company '{company}' seems open to a meeting or call. "
            f"Write a reply confirming your availability and suggesting a specific time slot next week. "
            f"Be flexible and propose Google Meet or Zoom. Keep it under 120 words."
        )
    elif reply_type == "interested":
        task = (
            f"The company '{company}' seems interested in the sponsorship. "
            f"Write a reply that thanks them, briefly reinforces your value proposition "
            f"(4K followers, 1.5M monthly views, active karting competitor), "
            f"and proposes next steps (a call or sending a formal media kit). Keep it under 150 words."
        )
    elif reply_type == "declined":
        task = (
            f"The company '{company}' has politely declined or is not available right now. "
            f"Write a gracious reply thanking them, leaving the door open for the future, "
            f"and asking if they know another contact or department that might be interested. "
            f"Keep it under 100 words."
        )
    else:
        task = (
            f"The company '{company}' replied to your sponsorship email. "
            f"Write a professional follow-up reply to move the conversation forward toward a deal. "
            f"Keep it under 150 words."
        )

    prompt = f"{task}\n\nTheir email:\n---\n{their_email_body[:1500]}\n---"

    resp = _get_claude().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def _wrap_html(plain_text: str) -> str:
    lines = plain_text.replace("\r\n", "\n").split("\n")
    html_lines = "<br>".join(l for l in lines)
    return f"<html><body style='font-family:Arial,sans-serif;font-size:15px;color:#222;max-width:680px;'>{html_lines}</body></html>"


def _detect_language(text: str) -> str:
    spanish_words = ["gracias", "hola", "estimado", "saludos", "disponible", "interesado", "podemos"]
    return "es" if any(w in text.lower() for w in spanish_words) else "en"


def _schedule_meeting(service, company: str, contact_email: str, notes: str = "") -> str | None:
    """Create a calendar event and return the event link."""
    # Find the next Monday from today
    today = date.today()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    meeting_date = today + timedelta(days=days_until_monday)

    event = create_meeting_event(
        summary=f"Sponsorship Meeting – {company}",
        attendee_email=contact_email,
        meeting_date=meeting_date,
        hour=DEFAULT_MEETING_HOUR,
        duration_minutes=DEFAULT_MEETING_DURATION_MINUTES,
        description=(
            f"Sponsorship discussion with {company}.\n"
            f"Pilot: {PILOT_NAME} ({PILOT_EMAIL})\n"
            f"{notes}"
        ),
    )
    return event.get("htmlLink")


def process_bot_replies(service, db: dict) -> list[dict]:
    """
    Scan Gmail for replies in threads tagged with BOT_LABEL_ID.
    For each unread reply from an external sender, generate and send a response.
    Returns a list of actions taken.
    """
    from sponsor_bot.gmail_client import search_threads

    actions = []
    query = f"label:{BOT_LABEL_ID.replace('Label_', 'Label_')} is:unread -from:me -from:mailer-daemon"
    # Gmail label query uses label name format
    query = f"label:Sponsor/🤖+Bot-Activo is:unread -from:me -from:mailer-daemon"

    threads = search_threads(service, query, max_results=50)
    print(f"[INFO] Found {len(threads)} threads with unread replies to process.")

    for thread_stub in threads:
        thread_id = thread_stub["id"]
        try:
            messages = get_thread_messages(service, thread_id)
        except Exception as e:
            print(f"[WARN] Could not get thread {thread_id}: {e}")
            continue

        # Find the last message not from us and unread
        their_message = None
        for msg in reversed(messages):
            label_ids = msg.get("labelIds", [])
            sender = get_header(msg, "from")
            if "UNREAD" in label_ids and PILOT_EMAIL not in sender:
                their_message = msg
                break

        if not their_message:
            continue

        # Extract context
        body = get_message_body(their_message)
        sender = get_header(their_message, "from")
        subject = get_header(their_message, "subject")
        msg_id = get_header(their_message, "message-id")

        # Identify company from subject or DB
        company = _extract_company_from_subject(subject)
        language = _detect_language(body)
        reply_type = _classify_reply(body)

        print(f"[INFO] Replying to {company} ({sender}) — type: {reply_type}")

        # Generate reply text
        reply_text = _generate_reply(company, body, reply_type, language)
        reply_html = _wrap_html(reply_text)

        # Extract sender's email address
        contact_email = _extract_email_from_sender(sender)

        # Create calendar event if meeting is requested
        calendar_link = None
        if reply_type == "meeting":
            try:
                calendar_link = _schedule_meeting(service, company, contact_email, body[:200])
                if calendar_link:
                    reply_text += f"\n\n(Meeting added to my calendar: {calendar_link})"
                    reply_html = _wrap_html(reply_text)
                    print(f"[INFO] Calendar event created: {calendar_link}")
            except Exception as e:
                print(f"[WARN] Calendar event failed: {e}")

        # Send the reply
        try:
            sent = send_email(
                service=service,
                to=contact_email,
                subject=f"Re: {subject}" if not subject.startswith("Re:") else subject,
                html_body=reply_html,
                reply_to_message_id=msg_id,
                reply_to_thread_id=thread_id,
                label_ids=[BOT_LABEL_ID],
            )
            mark_message_read(service, their_message["id"])
            update_status(db, contact_email, f"replied_{reply_type}")
            remove_from_pending(db, thread_id)

            actions.append({
                "thread_id": thread_id,
                "company": company,
                "contact": contact_email,
                "reply_type": reply_type,
                "calendar_link": calendar_link,
                "sent_message_id": sent.get("id"),
            })
        except Exception as e:
            print(f"[ERROR] Failed to send reply to {contact_email}: {e}")

    return actions


def _extract_company_from_subject(subject: str) -> str:
    """Extract company name from subjects like 'Re: Sponsorship Partnership – ... | CompanyName'"""
    match = re.search(r"\|\s*(.+)$", subject)
    if match:
        return match.group(1).strip()
    return subject.replace("Re: ", "").strip()[:60]


def _extract_email_from_sender(sender: str) -> str:
    """Extract email from 'Name <email@domain.com>' format."""
    match = re.search(r"<(.+?)>", sender)
    if match:
        return match.group(1).strip()
    return sender.strip()
