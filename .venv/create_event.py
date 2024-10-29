from googleapiclient.discovery import build
from quickstart import get_credentials
from datetime import datetime, timedelta

def create_google_calendar_event(event_name, event_date, event_location, event_description, event_start_time, event_end_time):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    # Convert the input strings to datetime objects
    start_datetime = datetime.strptime(f"{event_date} {event_start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{event_date} {event_end_time}", "%Y-%m-%d %H:%M")

    event = {
        'summary': event_name,
        'location': event_location,
        'description': event_description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/New_York',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')
if __name__ == '__main__':
   create_google_calendar_event()