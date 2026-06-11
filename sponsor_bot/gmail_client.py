"""Gmail API client using OAuth2 credentials from environment."""

import base64
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def _get_credentials() -> Credentials:
    """Build credentials from environment variables."""
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def get_service():
    return build("gmail", "v1", credentials=_get_credentials())


def send_email(
    service,
    to: str,
    subject: str,
    html_body: str,
    reply_to_message_id: str = None,
    reply_to_thread_id: str = None,
    label_ids: list[str] = None,
) -> dict:
    """Send an email and optionally add labels to the thread."""
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = os.environ.get("GMAIL_ADDRESS", "thi2012x@gmail.com")

    if reply_to_message_id:
        msg["In-Reply-To"] = reply_to_message_id
        msg["References"] = reply_to_message_id

    msg.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {"raw": raw}
    if reply_to_thread_id:
        body["threadId"] = reply_to_thread_id

    sent = service.users().messages().send(userId="me", body=body).execute()

    # Apply labels to the sent message
    if label_ids and sent.get("id"):
        service.users().messages().modify(
            userId="me",
            id=sent["id"],
            body={"addLabelIds": label_ids},
        ).execute()

    return sent


def search_threads(service, query: str, max_results: int = 50) -> list[dict]:
    threads = []
    page_token = None
    while len(threads) < max_results:
        params = {"userId": "me", "q": query, "maxResults": min(50, max_results - len(threads))}
        if page_token:
            params["pageToken"] = page_token
        resp = service.users().threads().list(**params).execute()
        threads.extend(resp.get("threads", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return threads


def get_thread_messages(service, thread_id: str) -> list[dict]:
    thread = service.users().threads().get(userId="me", id=thread_id, format="full").execute()
    return thread.get("messages", [])


def get_message_body(message: dict) -> str:
    """Extract plain text or HTML body from a Gmail message."""
    payload = message.get("payload", {})
    return _extract_body(payload)


def _extract_body(payload: dict) -> str:
    mime_type = payload.get("mimeType", "")
    if mime_type in ("text/plain", "text/html"):
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result
    return ""


def get_header(message: dict, name: str) -> str:
    headers = message.get("payload", {}).get("headers", [])
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def add_label_to_thread(service, thread_id: str, label_id: str):
    service.users().threads().modify(
        userId="me",
        id=thread_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def mark_message_read(service, message_id: str):
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()
