# NCLL Schedule Calendar Sync

This repository automatically syncs the NCLL game schedule from `permits_from_parks_summer.csv` to a public Google Calendar.

## Features

- ✅ Automatic sync when the CSV file is updated
- ✅ Daily scheduled sync
- ✅ Public calendar for all coaches, parents, and players
- ✅ Handles event creation, update, and deletion
- ✅ 1-hour popup reminders for all events
- ✅ All permit details in event description

## Setup Quickstart

1. **Google Cloud Setup**
   - Enable Google Calendar API for your project
   - Create a Service Account and download the key

2. **Google Calendar Setup**
   - Create a calendar (as scheduler@ncllball.com)
   - Share with the Service Account ("Make changes to events" permission)
   - Set it to public, copy the calendar ID

3. **Repository Secrets**
   - In GitHub, add:
     - `GOOGLE_CALENDAR_ID`: The calendar's ID (from Google Calendar settings)
     - `GOOGLE_SERVICE_ACCOUNT_KEY`: The full JSON content of your service account key
     - `CALENDAR_TIME_ZONE` (optional): America/Los_Angeles

4. **Workflow Files**
   - `.github/workflows/sync-calendar.yml`
   - `scripts/sync_calendar.py`
   - `scripts/requirements.txt`

5. **Test**
   - Edit and push `permits_from_parks_summer.csv`
   - Check Actions tab and verify success
   - Confirm events appear on the calendar

6. **Share Calendar**
   - Share the public URL or embed code with your league

## Troubleshooting

- **API errors:** Make sure the Google Calendar API is enabled in your Cloud project.
- **403 permission:** Make sure the Service Account has access to the calendar.
- **Datetime parse errors:** Make sure your CSV date/time format matches the script expectations, or update the script to handle your format.
- **Workflow fails:** Read the Actions tab logs for details.

## Maintainers

- For questions, open an issue on GitHub, or contact ncllball-admin.
