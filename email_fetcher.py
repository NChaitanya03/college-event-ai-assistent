import os
import json
import base64
import re
from datetime import datetime
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """
    Authenticates the user and returns the Gmail API service instance.
    Supports local files (token.json, credentials.json) as well as
    cloud environment variables (GMAIL_TOKEN_JSON, GMAIL_CREDENTIALS_JSON) for Vercel.
    """
    creds = None

    # 1. Try loading token from Environment Variable (Vercel deployment)
    env_token = os.environ.get('GMAIL_TOKEN_JSON')
    if env_token:
        try:
            token_dict = json.loads(env_token)
            creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
            print("Loaded credentials from GMAIL_TOKEN_JSON environment variable.")
        except Exception as e:
            print(f"Error parsing GMAIL_TOKEN_JSON env: {e}")

    # 2. Try loading token from local file (Local development)
    if not creds and os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")

    # 3. Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            print("Refreshing expired access token...")
            creds.refresh(Request())
            # Save to disk if writable (local dev)
            try:
                with open('token.json', 'w', encoding='utf-8') as token_file:
                    token_file.write(creds.to_json())
            except Exception:
                pass  # Read-only serverless filesystem
        except Exception as e:
            print(f"Failed to refresh token: {e}")
            creds = None

    # 4. If still no valid credentials, run OAuth flow (local dev only)
    if not creds:
        env_creds = os.environ.get('GMAIL_CREDENTIALS_JSON')
        if env_creds:
            try:
                creds_dict = json.loads(env_creds)
                flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error with GMAIL_CREDENTIALS_JSON: {e}")

        if not creds and os.path.exists('credentials.json'):
            print("Initiating local OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            try:
                with open('token.json', 'w', encoding='utf-8') as token_file:
                    token_file.write(creds.to_json())
            except Exception:
                pass

    if not creds:
        raise ValueError("No valid credentials found. Please set GMAIL_TOKEN_JSON or provide credentials.json.")

    return build('gmail', 'v1', credentials=creds)

def extract_body(payload):
    """Recursively extract plain text or HTML body from a message payload."""
    plain_text = ""
    html_text = ""

    def walk_parts(part):
        nonlocal plain_text, html_text
        mime = part.get('mimeType', '')
        body = part.get('body', {})
        data = body.get('data')

        if data:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if mime == 'text/plain':
                plain_text += decoded + "\n"
            elif mime == 'text/html':
                html_text += decoded + "\n"

        for subpart in part.get('parts', []):
            walk_parts(subpart)

    walk_parts(payload)

    if plain_text.strip():
        return plain_text.strip()
    if html_text.strip():
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    return ""

def get_user_profile():
    """Returns connected user profile info."""
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId='me').execute()
        return {
            'email': profile.get('emailAddress'),
            'messages_total': profile.get('messagesTotal'),
            'connected': True
        }
    except Exception as e:
        return {
            'email': None,
            'messages_total': 0,
            'connected': False,
            'error': str(e)
        }

def fetch_recent_emails(max_results=25, query=None):
    """
    Fetches the recent emails with complete headers and parsed bodies.
    """
    try:
        service = get_gmail_service()
        req_params = {'userId': 'me', 'maxResults': max_results}
        if query:
            req_params['q'] = query

        results = service.users().messages().list(**req_params).execute()
        messages = results.get('messages', [])

        email_items = []
        for m in messages:
            try:
                msg = service.users().messages().get(userId='me', id=m['id'], format='full').execute()
                payload = msg.get('payload', {})
                headers_list = payload.get('headers', [])
                headers = {h.get('name', '').lower(): h.get('value', '') for h in headers_list}

                from_header = headers.get('from', '')
                sender_name = from_header
                sender_email = from_header
                if '<' in from_header and '>' in from_header:
                    sender_name = from_header.split('<')[0].strip(' "\'')
                    sender_email = from_header.split('<')[1].split('>')[0].strip()

                body = extract_body(payload)
                if not body:
                    body = msg.get('snippet', '')

                internal_date = int(msg.get('internalDate', 0)) / 1000.0
                date_dt = datetime.fromtimestamp(internal_date) if internal_date > 0 else datetime.now()

                email_items.append({
                    'id': m['id'],
                    'thread_id': msg.get('threadId'),
                    'subject': headers.get('subject', '(No Subject)'),
                    'sender': sender_name or sender_email,
                    'sender_email': sender_email,
                    'date_header': headers.get('date', ''),
                    'timestamp': date_dt.isoformat(),
                    'snippet': msg.get('snippet', ''),
                    'body': body
                })
            except Exception as e:
                print(f"Error reading message {m.get('id')}: {e}")

        return email_items

    except HttpError as error:
        print(f"Gmail API HTTP error: {error}")
        return []
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

if __name__ == '__main__':
    profile = get_user_profile()
    print("User profile:", profile)
