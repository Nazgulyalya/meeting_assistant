import os
import base64
import re
import pickle
from dotenv import load_dotenv
load_dotenv()

EMAIL_REGEX = r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$'

def send_email(to: str, subject: str, body: str) -> dict:
    """Send email via Gmail API. Returns {success, error}."""
    # Validate email
    to = (to or "").strip()
    if not re.match(EMAIL_REGEX, to):
        return {"success": False, "error": f"Invalid email: '{to}'"}

    if not subject.strip():
        return {"success": False, "error": "Subject is empty"}

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from email.mime.text import MIMEText

        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        creds = None

        if os.path.exists("token_gmail.pickle"):
            with open("token_gmail.pickle", "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token_gmail.pickle", "wb") as f:
                pickle.dump(creds, f)

        service = build("gmail", "v1", credentials=creds)

        msg = MIMEText(body)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"success": True, "error": None}

    except Exception as e:
        return {"success": False, "error": str(e)}