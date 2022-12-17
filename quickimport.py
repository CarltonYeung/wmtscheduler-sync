import datetime
import os.path
import re

from pdf_regex_finder import PDFRegexFinder

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_id(service, name: str):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == name:
                return calendar_list_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    events = PDFRegexFinder.find_events('./schedule.pdf')

    try:
        service = build('calendar', 'v3', credentials=creds)
        calendar_id = get_calendar_id(service, 'WMT Scheduler')

        for event in events:
            # Delete existing events
            time_min = event.date.isoformat()
            time_max = (event.date + datetime.timedelta(days=1)).isoformat()

            existing_event = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max
            ).execute()

            for existing_event in existing_event['items']:
                delete_response = service.events().delete(calendarId=calendar_id, eventId=existing_event['id']).execute()
                if not delete_response:
                    print(f'Event deleted: {existing_event}')

            # Insert new event
            if event.shift != 'X':
                body = {
                    'summary': event.shift,
                    'start': {
                        'date': event.date.strftime('%Y-%m-%d')
                    },
                    'end': {
                        'date': event.date.strftime('%Y-%m-%d')
                    }
                }
                created_event = service.events().insert(calendarId=calendar_id, body=body).execute()
                print(f'Event created: {created_event}')

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
