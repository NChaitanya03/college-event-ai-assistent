import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Read-only scope is sufficient to fetch/read emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Authenticates the user and returns the Gmail API service instance."""
    creds = None
    # token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            print("Initiating authentication flow...")
            print("A browser window will open. Please log in and authorize the application.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w', encoding='utf-8') as token_file:
            token_file.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def fetch_recent_emails(max_results=10):
    """Fetches and displays details for the recent emails."""
    try:
        service = get_gmail_service()

        print(f"\nFetching recent {max_results} emails...\n")
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
            return

        print(f"{'='*80}")
        for idx, msg_meta in enumerate(messages, start=1):
            msg = service.users().messages().get(userId='me', id=msg_meta['id'], format='full').execute()
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])

            subject = "(No Subject)"
            sender = "(Unknown Sender)"
            date = "(Unknown Date)"

            for header in headers:
                name = header.get('name', '').lower()
                if name == 'subject':
                    subject = header.get('value', subject)
                elif name == 'from':
                    sender = header.get('value', sender)
                elif name == 'date':
                    date = header.get('value', date)

            snippet = msg.get('snippet', '')

            print(f"[{idx}] {subject}")
            print(f"    From: {sender}")
            print(f"    Date: {date}")
            print(f"    Snippet: {snippet}")
            print(f"{'-'*80}")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    fetch_recent_emails(max_results=10)

