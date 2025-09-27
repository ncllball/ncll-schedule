#!/usr/bin/env python3
"""
NCLL Schedule Sync to Google Calendar
Syncs permits_from_parks_summer.csv to Google Calendar
"""

import os
import csv
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
CSV_FILE = 'permits_from_parks_summer.csv'
CALENDAR_TIME_ZONE = os.environ.get('CALENDAR_TIME_ZONE', 'America/Los_Angeles')

def get_google_calendar_service():
    """Initialize Google Calendar API service."""
    try:
        creds_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
        if not creds_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY not found in environment")
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error initializing Google Calendar service: {e}")
        raise

def parse_csv_file(file_path: str) -> List[Dict]:
    """Parse CSV file and return list of events."""
    events = []
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('Date') and row.get('Start - End Time'):
                events.append(row)
    return events

def parse_datetime(date_str: str, time_str: str, timezone_str: str) -> tuple:
    """Parse date and time strings to datetime objects."""
    try:
        # Parse date (e.g., "May 31, 2023")
        date = datetime.strptime(date_str.strip(), "%b %d, %Y")
    except ValueError:
        try:
            date = datetime.strptime(date_str.strip(), "%B %d, %Y")
        except Exception as e:
            print(f"Error parsing date: {date_str} - {e}")
            return None, None

    # Auto-rewrite year to future if in the past (for demo/testing)
    if date.year < datetime.now().year:
        date = date.replace(year=datetime.now().year)
        print(f"Updated year for {date_str} to {date.year}")

    try:
        times = time_str.split(' - ')
        if len(times) != 2:
            print(f"Invalid time format: {time_str}")
            return None, None
        start_time_str = times[0].strip()
        end_time_str = times[1].strip()
        start_time = datetime.strptime(start_time_str, "%I:%M %p").time()
        end_time = datetime.strptime(end_time_str, "%I:%M %p").time()
        start_datetime = datetime.combine(date.date(), start_time)
        end_datetime = datetime.combine(date.date(), end_time)
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)
        tz = pytz.timezone(timezone_str)
        start_datetime = tz.localize(start_datetime)
        end_datetime = tz.localize(end_datetime)
        return start_datetime, end_datetime
    except Exception as e:
        print(f"Error parsing datetime: {date_str} {time_str} - {e}")
        return None, None

def create_event_id(row: Dict) -> str:
    """Create a unique event ID based on event data."""
    unique_str = f"{row['Date']}_{row['Start - End Time']}_{row['Facility/Equipment/Instructor']}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def create_calendar_event(row: Dict) -> Optional[Dict]:
    try:
        start_dt, end_dt = parse_datetime(
            row['Date'],
            row['Start - End Time'],
            CALENDAR_TIME_ZONE
        )
        if not start_dt or not end_dt:
            print(f"Could not parse datetime for row: {row}")
            return None
        facility = row['Facility/Equipment/Instructor']
        title = f"NCLL Game - {facility}"
        description_lines = [
            f"Facility: {facility}",
            f"Date: {row['Date']} ({row.get('Day','')})",
            f"Time: {row['Start - End Time']}",
            f"Permit #: {row.get('Permit#','')}",
        ]
        if row.get('Setup - Ready Time'):
            description_lines.append(f"Setup Time: {row['Setup - Ready Time']}")
        if row.get('Attend/Qty'):
            description_lines.append(f"Attendance/Quantity: {row['Attend/Qty']}")
        description = '\n'.join(description_lines)
        event = {
            'id': create_event_id(row),
            'summary': title,
            'description': description,
            'location': facility,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': CALENDAR_TIME_ZONE,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': CALENDAR_TIME_ZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }
        return event
    except Exception as e:
        print(f"Error creating event from row: {row}, Error: {e}")
        return None

def get_existing_events(service, calendar_id: str) -> Dict[str, Dict]:
    existing_events = {}
    try:
        page_token = None
        while True:
            events_result = service.events().list(
                calendarId=calendar_id,
                pageToken=page_token,
                maxResults=2500,
                showDeleted=False
            ).execute()
            events = events_result.get('items', [])
            for event in events:
                if event.get('id'):
                    existing_events[event['id']] = event
            page_token = events_result.get('nextPageToken')
            if not page_token:
                break
    except HttpError as error:
        print(f'An error occurred getting existing events: {error}')
    return existing_events

def sync_events_to_calendar(service, calendar_id: str, csv_events: List[Dict]):
    print("Fetching existing calendar events...")
    existing_events = get_existing_events(service, calendar_id)
    print(f"Found {len(existing_events)} existing events")
    created = 0
    updated = 0
    deleted = 0
    errors = 0
    new_events = {}
    for row in csv_events:
        event = create_calendar_event(row)
        if event:
            new_events[event['id']] = event
    print(f"Parsed {len(new_events)} events from CSV")
    for event_id, event in new_events.items():
        try:
            if event_id in existing_events:
                existing = existing_events[event_id]
                if (existing.get('summary') != event.get('summary') or
                    existing.get('start') != event.get('start') or
                    existing.get('end') != event.get('end') or
                    existing.get('location') != event.get('location')):
                    service.events().update(
                        calendarId=calendar_id,
                        eventId=event_id,
                        body=event
                    ).execute()
                    updated += 1
                    print(f"Updated: {event['summary']} on {event['start']['dateTime']}")
            else:
                service.events().insert(
                    calendarId=calendar_id,
                    body=event
                ).execute()
                created += 1
                print(f"Created: {event['summary']} on {event['start']['dateTime']}")
        except HttpError as error:
            errors += 1
            print(f"Error processing event {event.get('summary', 'Unknown')}: {error}")
    for event_id in existing_events:
        if event_id not in new_events:
            try:
                service.events().delete(
                    calendarId=calendar_id,
                    eventId=event_id
                ).execute()
                deleted += 1
                print(f"Deleted event: {event_id}")
            except HttpError as error:
                errors += 1
                print(f"Error deleting event {event_id}: {error}")
    print("\n" + "="*50)
    print("SYNC SUMMARY")
    print("="*50)
    print(f"Events created: {created}")
    print(f"Events updated: {updated}")
    print(f"Events deleted: {deleted}")
    print(f"Errors: {errors}")
    print(f"Total events in calendar: {len(new_events)}")
    print("="*50)

def main():
    try:
        calendar_id = os.environ.get('GOOGLE_CALENDAR_ID')
        if not calendar_id:
            raise ValueError("GOOGLE_CALENDAR_ID not found in environment")
        print(f"Starting sync for calendar: {calendar_id}")
        print(f"Using timezone: {CALENDAR_TIME_ZONE}")
        service = get_google_calendar_service()
        print(f"Reading CSV file: {CSV_FILE}")
        csv_events = parse_csv_file(CSV_FILE)
        print(f"Found {len(csv_events)} rows in CSV")
        sync_events_to_calendar(service, calendar_id, csv_events)
        print("\nSync completed successfully!")
    except Exception as e:
        print(f"Fatal error during sync: {e}")
        raise

if __name__ == "__main__":
    main()
