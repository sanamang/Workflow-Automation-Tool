from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from typing import Dict, Any

class GoogleService:
    def __init__(self):
        self.SCOPES = {
            'sheets': ['https://www.googleapis.com/auth/spreadsheets'],
            'calendar': ['https://www.googleapis.com/auth/calendar']
        }
        self.credentials = None

    def get_credentials(self, service_type: str) -> Credentials:
        """Get or refresh Google API credentials."""
        if os.path.exists(f'token_{service_type}.pickle'):
            with open(f'token_{service_type}.pickle', 'rb') as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES[service_type])
                self.credentials = flow.run_local_server(port=0)
            
            with open(f'token_{service_type}.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)

        return self.credentials

    def update_google_sheet(self, spreadsheet_id: str, sheet_name: str, data: Dict[str, Any]) -> bool:
        """Update Google Sheet with provided data."""
        try:
            creds = self.get_credentials('sheets')
            service = build('sheets', 'v4', credentials=creds)
            
            # Prepare the data for update
            values = [[data.get(key) for key in data.keys()]]
            body = {'values': values}
            
            # Update the sheet
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error updating Google Sheet: {str(e)}")
            return False

    def create_calendar_event(self, calendar_id: str, event_data: Dict[str, Any]) -> bool:
        """Create a new event in Google Calendar."""
        try:
            creds = self.get_credentials('calendar')
            service = build('calendar', 'v3', credentials=creds)
            
            event = {
                'summary': event_data.get('title'),
                'description': event_data.get('description'),
                'start': {
                    'dateTime': event_data.get('start'),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event_data.get('end'),
                    'timeZone': 'UTC',
                },
            }
            
            service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error creating calendar event: {str(e)}")
            return False 