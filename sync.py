import configparser
import glob
import os.path
import re

from datetime import datetime, timedelta
from typing import Tuple

from model import Event
from pdf_regex_finder import PDFRegexFinder

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SHIFT_LENGTH_HOURS = 8
ADMIN_SHIFT_LENGTH_HOURS = 8.5
FLEX_HOURS = 0.5
CONFIG_CALENDAR_NAME = "GoogleCalendarName"
CONFIG_CREDENTIALS_FILE = "GoogleOAuthCredentials"
CONFIG_PDF_GLOB = "SchedulePDFGlobPattern"


def get_calendar_id(service, name: str) -> str:
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list["items"]:
            if calendar_list_entry["summary"] == name:
                return calendar_list_entry["id"]
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break


def get_credentials(CONFIG_CREDENTIALS_FILE: str) -> Credentials:
    CACHED_TOKEN_FILE = "token.json"
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(CACHED_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(CACHED_TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CONFIG_CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(CACHED_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def get_shift_start_end(event: Event) -> Tuple[datetime, datetime]:
    start, end = None, None

    try:
        start = event.date + timedelta(hours=int(re.search(r"(\d+)", event.shift).group()))
        start -= timedelta(hours=FLEX_HOURS)
        end = start + timedelta(
            hours=ADMIN_SHIFT_LENGTH_HOURS if "@" in event.shift else SHIFT_LENGTH_HOURS
        )
    except:
        start = event.date
        end = start

    return start, end


def get_config() -> configparser.SectionProxy:
    SETTINGS_FILE = "settings.ini"

    config = configparser.ConfigParser()
    config.optionxform = str
    if not os.path.exists(SETTINGS_FILE):
        config["DEFAULT"] = {
            CONFIG_CALENDAR_NAME: "WMT Scheduler",
            CONFIG_CREDENTIALS_FILE: "credentials.json",
            CONFIG_PDF_GLOB: "./My Schedule*.pdf",
        }

        with open(SETTINGS_FILE, "w") as config_file:
            config.write(config_file)

    config.read(SETTINGS_FILE)
    print("Using settings.ini:")
    for key in config["DEFAULT"]:
        print(f"{key}: {config['DEFAULT'][key]}")
    return config["DEFAULT"]


def main():
    config = get_config()
    creds = get_credentials(config[CONFIG_CREDENTIALS_FILE])

    for file in glob.glob(config[CONFIG_PDF_GLOB]):

        events = PDFRegexFinder.find_events(file)

        try:
            service = build("calendar", "v3", credentials=creds)
            calendar_id = get_calendar_id(service, config[CONFIG_CALENDAR_NAME])

            for event in events:
                # Delete existing event
                existing_event = (
                    service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=event.date.isoformat(),
                        timeMax=(event.date + timedelta(days=1)).isoformat(),
                    )
                    .execute()
                )

                for existing_event in existing_event["items"]:
                    delete_response = (
                        service.events()
                        .delete(calendarId=calendar_id, eventId=existing_event["id"])
                        .execute()
                    )
                    # if not delete_response:
                    #     print(f"Deleted: {existing_event}")

                # Insert new event
                start, end = get_shift_start_end(event)
                body = {
                    "summary": event.shift,
                    "start": {"dateTime": start.isoformat()},
                    "end": {"dateTime": end.isoformat()},
                }
                created_event = (
                    service.events()
                    .insert(calendarId=calendar_id, body=body)
                    .execute()
                )
                if created_event:
                    print(f"Created: {event.shift} on {start}")


        except HttpError as error:
            print("An error occurred: %s" % error)


if __name__ == "__main__":
    main()
