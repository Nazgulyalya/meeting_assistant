def create_event(title: str, description: str, start: str, end: str, attendees: list) -> bool:
    """Create Google Calendar event."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import pickle, os

        SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
        creds = None

        if os.path.exists("token_calendar.pickle"):
            with open("token_calendar.pickle", "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token_calendar.pickle", "wb") as f:
                pickle.dump(creds, f)

        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
            "attendees": [{"email": e} for e in attendees]
        }
        service.events().insert(calendarId="primary", body=event).execute()
        return True

    except Exception as e:
        print(f"Calendar error: {e}")
        return False