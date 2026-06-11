"""Google Calendar API client."""

import os
from datetime import date, datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from sponsor_bot.config import TIMEZONE, DEFAULT_MEETING_HOUR, DEFAULT_MEETING_DURATION_MINUTES

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _get_credentials() -> Credentials:
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


def get_calendar_service():
    return build("calendar", "v3", credentials=_get_credentials())


def create_meeting_event(
    summary: str,
    attendee_email: str,
    meeting_date: date,
    hour: int = DEFAULT_MEETING_HOUR,
    duration_minutes: int = DEFAULT_MEETING_DURATION_MINUTES,
    description: str = "",
) -> dict:
    service = get_calendar_service()

    start_dt = datetime(meeting_date.year, meeting_date.month, meeting_date.day, hour, 0, 0)
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
        "attendees": [{"email": attendee_email}],
        "conferenceData": {
            "createRequest": {
                "requestId": f"sponsor-{meeting_date.isoformat()}-{attendee_email[:10]}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 60},
                {"method": "popup", "minutes": 15},
            ],
        },
        "colorId": "11",  # Tomato red
    }

    event = service.events().insert(
        calendarId="primary",
        body=event_body,
        conferenceDataVersion=1,
        sendUpdates="all",
    ).execute()
    return event
