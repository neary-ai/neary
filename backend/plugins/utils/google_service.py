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
from datetime import datetime, timedelta
import pytz

import talon
from talon import quotations
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.services.credential_manager import CredentialManager

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
        email_dict["sent_time"] = datetime.fromisoformat(
            email_dict["sent_time"])
        return cls(**email_dict)

    def __str__(self):
        return f"From: {self.sender}\nSubject: {self.subject}\nSent: {self.sent_time}\n\n{self.body}"

class GoogleService:

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        self.creds = None

    async def authenticate(self):
        credential_manager = await CredentialManager.create('google_calendar')
        credentials = await credential_manager.get_credentials()
        try:
            self.creds = Credentials(
                credentials['access_token'],
            )
            return True
        except Exception as e:
            print(e)
            return False

    def get_new_emails(self, search_term=None, results=25):
        emails = []
        query = f'in:inbox'
        query += f' {search_term}' if search_term else ''
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            messages = service.users().messages().list(
                userId='me', maxResults=results, q=query).execute().get('messages', [])

            def get_body(payload):
                body = ''
                if payload['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(
                        payload['body']['data']).decode('utf-8')
                elif 'parts' in payload:
                    for part in payload['parts']:
                        body = get_body(part)
                        if body:
                            break
                return body

            for msg_info in messages:
                msg = service.users().messages().get(
                    userId='me', id=msg_info['id']).execute()
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
            message = service.users().messages().get(
                userId='me', id=message_id, format='full').execute()
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
                    body = base64.urlsafe_b64decode(
                        payload['body']['data']).decode('utf-8')
                elif 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(
                                part['body']['data']).decode('utf-8')
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
                attach.add_header('Content-Disposition',
                                  f'attachment; filename={filename}')
                message.attach(attach)

            create_message = {
                'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
            }
            send_message = (service.users().messages().send(
                userId="me", body=create_message).execute())
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
            send_message = (service.users().messages().send(
                userId="me", body=create_message).execute())
            print(F'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message

    def create_calendar_event(self, event_title, event_description, start_time, end_time, attendees):
        calendar_service = build('calendar', 'v3', credentials=self.creds)
        event_data = {
            'summary': event_title,
            'description': event_description,
            'start': {
                'dateTime': start_time
            },
            'end': {
                'dateTime': end_time
            },
            'attendees': attendees
        }

        try:
            print(event_data)
            event = calendar_service.events().insert(
                calendarId='primary', body=event_data, sendUpdates='all').execute()
            link = event.get("htmlLink")
            print(f'Event created: {link}')
            return link
        except HttpError as error:
            print(f'An error occurred: {error}')
            return 'Creating event.'


    def get_calendar_events(self, days=7, filter_recurring=True):
        calendar_service = build('calendar', 'v3', credentials=self.creds)
        try:
            # Get the calendar metadata
            calendar = calendar_service.calendars().get(calendarId='primary').execute()

            # Get the timezone of the calendar
            calendar_tz = pytz.timezone(calendar['timeZone'])

            # Get current time in the calendar's timezone
            current_time = datetime.now(calendar_tz)

            # Convert cutoff_date to RFC3339 format in the calendar's timezone
            cutoff_datetime = current_time + timedelta(days=days)
            cutoff_rfc3339 = cutoff_datetime.isoformat()

            # Get current time in RFC3339 format in the calendar's timezone
            current_time_rfc3339 = current_time.isoformat()

            # Call the Calendar API to fetch events
            events_result = calendar_service.events().list(calendarId='primary', timeMin=current_time_rfc3339, timeMax=cutoff_rfc3339,
                                                        singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No events found.')
                return None
            else:
                events = self.filter_recurring_events(
                    events) if filter_recurring else events
                clean_events = [self.extract_event_info(
                    event) for event in events]
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
