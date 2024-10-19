from googleapiclient.discovery import build
from quickstart import get_credentials

def create_event():
   creds = get_credentials()
   service = build('calendar', 'v3', credentials=creds)

   event = {
       'summary': 'Meeting with Team',
       'location': 'Conference Room 1',
       'description': 'Discuss project progress',
       'start': {
           'dateTime': '2024-10-20T09:00:00',
           'timeZone': 'America/Los_Angeles',
       },
       'end': {
           'dateTime': '2024-10-20T10:00:00',
           'timeZone': 'America/Los_Angeles',
       },
   }

   event = service.events().insert(calendarId='primary', body=event).execute()
   print(f'Event created: {event.get("htmlLink")}')

if __name__ == '__main__':
   create_event()