import os
import pickle
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/contacts']

def get_credentials():
    """Gets valid user credentials from storage.
    
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def remove_january_first_birthdays():
    """Removes January 1st birthdays from Google Contacts."""
    creds = get_credentials()
    service = build('people', 'v1', credentials=creds)
    
    # Get all contacts
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=1000,
        personFields='birthdays,names'
    ).execute()
    
    connections = results.get('connections', [])
    
    for person in connections:
        birthdays = person.get('birthdays', [])
        for birthday in birthdays:
            date = birthday.get('date', {})
            if date.get('month') == 1 and date.get('day') == 1:
                # Remove the birthday
                birthday['date'] = None
                # Update the contact
                service.people().updateContact(
                    resourceName=person['resourceName'],
                    updatePersonFields='birthdays',
                    body={'birthdays': birthdays}
                ).execute()
                print(f"Removed January 1st birthday for {person.get('names', [{}])[0].get('displayName', 'Unknown')}")

if __name__ == '__main__':
    remove_january_first_birthdays() 