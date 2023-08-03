import re
import json
import base64
import os.path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dataclasses import dataclass
from dateutil.parser import parse
from datetime import datetime, timedelta, timezone

import talon
from talon import quotations
from tortoise.exceptions import DoesNotExist
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from backend.models import AuthCredentialModel

talon.init()

@dataclass
class Email:
    id: str
    sender: str
    subject: str
    body: str
    sent_time: datetime

    def __init__(self, id, sender, subject, body, sent_time):
        self.id = id
        self.sender = sender
        self.subject = subject
        self.body = body
        self.sent_time = sent_time

    def to_json(self):
        return json.dumps({"id": self.id,
                           "sender": self.sender,
                           "subject": self.subject,
                           "body": self.body,
                           "sent_time": self.sent_time.isoformat()})

    @classmethod
    def from_json(cls, json_str):
        email_dict = json.loads(json_str)
        email_dict["sent_time"] = datetime.fromisoformat(email_dict["sent_time"])
        return cls(**email_dict)

    def __str__(self):
        return f"From: {self.sender}\nSubject: {self.subject}\nSent: {self.sent_time}\n\n{self.body}"

class GoogleService:

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        self.creds = None

    async def authenticate(self):
        auth_url = None
        success = False
        
        try:
            client_id, client_secret = self.load_client_info('credentials/google_oauth.json')
            auth_credential = await AuthCredentialModel.get(provider="gmail", auth_type="oauth2")
            access_token = auth_credential.data["access_token"]
            refresh_token = auth_credential.data["refresh_token"]
            expires_at = datetime.fromisoformat(auth_credential.data["expires_at"])
            scopes = auth_credential.data["scopes"]
            
            self.creds = Credentials(
                access_token,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes
            )
            
            if expires_at <= datetime.utcnow():
                self.creds.refresh(Request())

                # Update the AuthCredentialModel with fresh token
                auth_credential.data["access_token"] = self.creds.token
                auth_credential.data["expires_at"] = self.creds.expiry.isoformat()
                await auth_credential.save()

            success = True

        except DoesNotExist:
            redirect_uri = os.environ.get("BASE_URL", "http://localhost:8000") + "/api/oauth2/callback"
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/google_oauth.json', self.SCOPES,
                redirect_uri=redirect_uri
            )

            auth_url, _ = flow.authorization_url(prompt='consent')
        
        return success, auth_url

    def load_client_info(self, credentials_file):
        try:
            with open(credentials_file, 'r') as file:
                credentials_data = json.load(file)
            return credentials_data['web']['client_id'], credentials_data['web']['client_secret']
        except FileNotFoundError:
            raise Exception("""Google OAuth credentials file not found.  [See here for setup instructions](https://github.com/neary-ai/neary/blob/main/docs/calendar_chat.md).""")

    def get_new_emails(self, search_term=None, results=25):
        emails = []
        query = f'in:inbox'
        query += f' {search_term}' if search_term else ''
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            messages = service.users().messages().list(userId='me', maxResults=results, q=query).execute().get('messages', [])
            
            def get_body(payload):
                body = ''
                if payload['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                elif 'parts' in payload:
                    for part in payload['parts']:
                        body = get_body(part)
                        if body:
                            break
                return body
            
            for msg_info in messages:
                msg = service.users().messages().get(userId='me', id=msg_info['id']).execute()
                message_id = msg_info['id']
                payload = msg['payload']
                subject, sender, body, date = '', '', '', ''
                for header in payload['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    if header['name'] == 'From':
                        sender = header['value']
                    if header['name'] == 'Date':
                        date = header['value']
                        date = re.sub(r'\s*\([A-Za-z]+\)$', '', date)

                body = get_body(payload)

                if subject and sender and body:
                    date_obj = parse(date)
                    email = Email(message_id, sender, subject, body, date_obj)
                    emails.append(email)
            return emails
        except HttpError as error:
            print(F'An error occurred: {error}')

    def get_thread_messages(self, message_id):
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
            thread_id = message['threadId']
            thread = service.users().threads().get(userId='me', id=thread_id).execute()

            messages = []
            for msg in thread['messages']:
                payload = msg['payload']
                sender, subject, date, body, references = '', '', '', '', ''
                for header in payload['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    if header['name'] == 'From':
                        sender = header['value']
                    if header['name'] == 'To':
                        recipient = header['value']
                    if header['name'] == 'Date':
                        date = header['value']
                        date = re.sub(r'\s*\([A-Za-z]+\)$', '', date)
                    if header['name'] == 'References':
                        references = header['value']
                    if header['name'] == 'Message-ID':
                        message_id = header['value']

                if payload['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                elif 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break

                # Clean up the body using talon
                clean_body = quotations.extract_from_plain(body)

                messages.append({
                    'thread_id': thread_id,
                    'message_id': message_id,
                    'sender': sender,
                    'recipient': recipient,
                    'subject': subject,
                    'date': date,
                    'body': clean_body,
                    'references': references
                })

            print(f'\n\nReturning messages from thread {messages}\n\n')
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def send_email(self, recipient, subject, body, attachment_file_path=None):
        try:
            attachment = attachment_file_path
            service = build('gmail', 'v1', credentials=self.creds)
            message = MIMEMultipart()
            message.attach(MIMEText(body, 'plain'))
            message['To'] = recipient
            message['Subject'] = subject
            message['From'] = f'Larry <me>'

            if attachment:
                with open(attachment, "rb") as f:
                    attach = MIMEBase('application', 'octet-stream')
                    attach.set_payload(f.read())
                encoders.encode_base64(attach)
                filename = os.path.basename(attachment)
                attach.add_header('Content-Disposition', f'attachment; filename={filename}')
                message.attach(attach)

            create_message = {
                'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
            }
            send_message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message

    def send_reply(self, thread_id, reply_from, recipient, subject, body, in_reply_to=None, references=None):
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            message = MIMEText(body)
            message['To'] = recipient
            message['Subject'] = subject
            message['From'] = reply_from
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
            if references:
                message['References'] = references
            create_message = {
                'raw': base64.urlsafe_b64encode(message.as_bytes()).decode(),
                'threadId': thread_id
            }
            send_message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message

    def create_calendar_event(self, event_title, event_description, start_time, end_time, attendees, tz):
        calendar_service = build('calendar', 'v3', credentials=self.creds)
        event_data = {
            'summary': event_title,
            'description': event_description,
            'start': {
                'dateTime': start_time,
                'timeZone': tz,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': tz,
            },
            'attendees': attendees
        }

        try:
            print(event_data)
            event = calendar_service.events().insert(calendarId='primary', body=event_data, sendUpdates='all').execute()
            link = event.get("htmlLink")
            print(f'Event created: {link}')
            return link
        except HttpError as error:
            print(f'An error occurred: {error}')
            return 'Creating event.'

    def get_calendar_events(self, days=7, filter_recurring=True):

        calendar_service = build('calendar', 'v3', credentials=self.creds)
        try:
            # Convert cutoff_date to RFC3339 format
            cutoff_datetime = datetime.now() + timedelta(days=days)
            cutoff_rfc3339 = cutoff_datetime.replace(tzinfo=timezone.utc).isoformat()

            # Get current time in RFC3339 format
            current_time_rfc3339 = datetime.now(timezone.utc).isoformat()

            # Call the Calendar API to fetch events
            events_result = calendar_service.events().list(calendarId='primary', timeMin=current_time_rfc3339, timeMax=cutoff_rfc3339,
                                                            singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No events found.')
                return None
            else:
                events = self.filter_recurring_events(events) if filter_recurring else events
                clean_events = [self.extract_event_info(event) for event in events]
                for clean_event in clean_events:
                    print(clean_event)
                return clean_events
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def filter_recurring_events(self, events):
        filtered_events = []
        recurring_event_ids = set()

        for event in events:
            recurring_event_id = event.get('recurringEventId')

            if recurring_event_id:
                if recurring_event_id not in recurring_event_ids:
                    recurring_event_ids.add(recurring_event_id)
                    filtered_events.append(event)
            else:
                filtered_events.append(event)

        return filtered_events

    def extract_event_info(self, event):
        event_id = event.get('id', '')
        summary = event.get('summary', '')
        location = event.get('location', '')

        start_time = event['start'].get('dateTime', event['start'].get('date'))
        end_time = event['end'].get('dateTime', event['end'].get('date'))

        attendees = event.get('attendees', [])
        attendee_emails = [attendee.get('email', '') for attendee in attendees]

        hangout_link = event.get('hangoutLink', '')
        description = event.get('description', '')

        clean_event = {
            'id': event_id,
            'summary': summary,
            'location': location,
            'start_time': start_time,
            'end_time': end_time,
            'attendees': attendee_emails,
            'hangout_link': hangout_link,
            'description': description
        }

        return clean_event