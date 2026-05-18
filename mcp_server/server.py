"""Custom MCP server exposing Gmail and Calendar tools.

This server implements the Model Context Protocol (MCP) over stdio.
It is owned by this project and runs as a subprocess invoked by the MCP client.
"""

import asyncio
import os
import sys
import base64
import re
import pickle
from email.mime.text import MIMEText

# Make sure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

# --- Initialize MCP server ---
mcp = FastMCP("meeting-assistant-mcp")

EMAIL_REGEX = r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$'


def _get_google_credentials(scopes: list, token_file: str):
    """Helper to load or refresh Google OAuth credentials."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
    return creds


# --- Tool: send_email ---
@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """Send a follow-up email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Plain-text email body
    """
    to = (to or "").strip()
    if not re.match(EMAIL_REGEX, to):
        return {"success": False, "error": f"Invalid email: '{to}'"}
    if not subject.strip():
        return {"success": False, "error": "Subject is empty"}

    try:
        from googleapiclient.discovery import build
        creds = _get_google_credentials(
            scopes=["https://www.googleapis.com/auth/gmail.send"],
            token_file="token_gmail.pickle"
        )
        service = build("gmail", "v1", credentials=creds)

        msg = MIMEText(body)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Tool: create_calendar_event ---
@mcp.tool()
def create_calendar_event(
    title: str,
    description: str,
    start: str,
    end: str,
    attendees: list[str]
) -> dict:
    """Create a follow-up meeting event on Google Calendar.

    Args:
        title: Event title
        description: Event description body
        start: ISO datetime string for start (e.g. '2024-06-01T10:00:00')
        end: ISO datetime string for end
        attendees: List of email addresses to invite
    """
    if not title.strip():
        return {"success": False, "error": "Title is empty"}

    try:
        from googleapiclient.discovery import build
        creds = _get_google_credentials(
            scopes=["https://www.googleapis.com/auth/calendar.events"],
            token_file="token_calendar.pickle"
        )
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
            "attendees": [{"email": e.strip()} for e in attendees if e.strip()]
        }
        service.events().insert(calendarId="primary", body=event).execute()
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run MCP server over stdio
    mcp.run()