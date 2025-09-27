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
    print(f"Opening CSV file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        # Read first few lines for debugging
        file.seek(0)
        first_lines = file.readlines()[:3]
        print(f"First 3 lines of CSV:")
        for i, line in enumerate(first_lines):
            print(f"  Line {i}: {line.strip()}")
        
        # Reset to beginning
        file.seek(0)
        reader = csv.DictReader(file)
        
        print(f"CSV Headers detected: {reader.fieldnames}")
        
        for row_num, row in enumerate(reader, 1):
            # Debug first row
            if row_num == 1:
                print(f"First data row: {row}")
            
            # Check for the actual column names in your CSV
            if row.get('Date') and row.get('Start - End Time'):
                events.append(row)
            else:
                print(f"Skipping row {row_num}: Missing Date or Start - End Time")
    
    print(f"Total events parsed: {len(events)}")
    return events

def parse_datetime(date_str: str, time_str: str, timezone_str: str) -> tuple:
    """Parse date and time strings to datetime objects."""
    try:
        # Remove quotes if present
        date_str = date_str.strip().strip('"')
        time_str = time_str.strip().strip('"')
        
        # Try different date formats
        date = None
        for date_format in ["%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"]:
            try:
                date = datetime.strptime(date_str, date_format)
                break
            except ValueError:
                continue
        
        if not date:
            print(f"Could not parse date: {date_str}")
            return None, None
        
        # Parse time range (e.g., "03:00 PM - 08:15 PM")
        times = time_str.split(' - ')
        if len(times) != 2:
            print(f"Invalid time format: {time_str}")
            return None, None
        
        start_time_str = times[0].strip()
        end_time_str = times[1].strip()
        
        # Parse times
        start_time = datetime.strptime(start_time_str, "%I:%M %p").time()
        end_time = datetime.strptime(end_time_str, "%I:%M %p").time()
        
        start_datetime = datetime.combine(date.date(), start_time)
        end_datetime = datetime.combine(date.date(), end_time)
        
        # Handle end time past midnight
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)
        
        # Apply timezone
        tz = pytz.timezone(timezone_str)
        start_datetime = tz.localize(start_datetime)
        end_datetime = tz.localize(end_datetime)
        
        return start_datetime, end_datetime
    except Exception as e:
        print(f"Error parsing datetime: {date_str} {time_str} - {e}")
        return None, None

def create_event_id(row: Dict) -> str:
    """Create a unique event ID based on event data."""
    # Remove quotes from values
    date = row.get('Date', '').strip('"')
    time = row.get('Start - End Time', '').strip('"')
    facility = row.get('Facility/Equipment/Instructor', '').strip('"')
    unique_str = f"{date}_{time}_{facility}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def create_calendar_event(row: Dict) -> Optional[Dict]:
    """Convert CSV row to Google Calendar event."""
    try:
        # Remove quotes from all values
        date_str = row.get('Date', '').strip('"')
        time_str = row.get('Start - End Time', '').strip('"')
        facility = row.get('Facility/Equipment/Instructor', '').strip('"')
        permit_num = row.get('Permit#', '').strip('"')
        day = row.get('Day', '').strip('"')
        attend_qty = row.get('Attend/Qty', '').strip('"')
        
        start_dt, end_dt = parse_datetime(date_str, time_str, CALENDAR_TIME_ZONE)
        
        if not start_dt or not end_dt:
            return None
        
        # Create event title
        title = f"NCLL Game - {facility}"
        
        # Create description
        description_lines = [
            f"Facility: {facility}",
            f"Date: {date_str} ({day})",
            f"Time: {time_str}",
            f"Permit #: {permit_num}",
        ]
        
        if attend_qty:
            description_lines.append(f"Attendance/Quantity: {attend_qty}")
        
        description = '\n'.join(description_lines)
        
        # Create the event
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
    """Get all existing events from the calendar."""
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
    """Sync events from CSV to Google Calendar."""
    
    print("Fetching existing calendar events...")
    existing_events = get_existing_events(service, calendar_id)
    print(f"Found {len(existing_events)} existing events")
    
    # Track statistics
    created = 0
    updated = 0
    deleted = 0
    errors = 0
    
    # Convert CSV rows to calendar events
    new_events = {}
    for row in csv_events:
        event = create_calendar_event(row)
        if event:
            new_events[event['id']] = event
    
    print(f"Parsed {len(new_events)} valid events from CSV")
    
    # Create or update events
    for event_id, event in new_events.items():
        try:
            if event_id in existing_events:
                # Update existing event if changed
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
                    print(f"Updated: {event['summary']}")
            else:
                # Create new event
                service.events().insert(
                    calendarId=calendar_id,
                    body=event
                ).execute()
                created += 1
                print(f"Created: {event['summary']}")
                
        except HttpError as error:
            errors += 1
            print(f"Error processing event {event.get('summary', 'Unknown')}: {error}")
    
    # Delete events not in CSV
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
    
    # Print summary
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
    """Main function to sync CSV to Google Calendar."""
    try:
        # Check for required environment variables
        calendar_id = os.environ.get('GOOGLE_CALENDAR_ID')
        if not calendar_id:
            raise ValueError("GOOGLE_CALENDAR_ID not found in environment")
        
        print(f"Starting sync for calendar: {calendar_id}")
        print(f"Using timezone: {CALENDAR_TIME_ZONE}")
        
        # Initialize Google Calendar service
        service = get_google_calendar_service()
        
        # Parse CSV file
        print(f"Reading CSV file: {CSV_FILE}")
        csv_events = parse_csv_file(CSV_FILE)
        print(f"Found {len(csv_events)} rows in CSV")
        
        if len(csv_events) == 0:
            print("WARNING: No events found in CSV file!")
            print("Check that the CSV has 'Date' and 'Start - End Time' columns")
        else:
            # Sync events
            sync_events_to_calendar(service, calendar_id, csv_events)
        
        print("\nSync completed successfully!")
        
    except Exception as e:
        print(f"Fatal error during sync: {e}")
        raise

if __name__ == "__main__":
    main()
