import os
import pickle
import time
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

def get_all_contacts(service):
    """Gets all contacts using pagination."""
    all_connections = []
    page_token = None
    
    while True:
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=1000,
            pageToken=page_token,
            personFields='birthdays,names,metadata'
        ).execute()
        
        connections = results.get('connections', [])
        all_connections.extend(connections)
        
        # Get the next page token
        page_token = results.get('nextPageToken')
        if not page_token:
            break
            
        print(f"Fetched {len(all_connections)} contacts so far...")
    
    return all_connections

def find_january_first_birthdays(dry_run=True):
    """Finds contacts with January 1st birthdays.
    
    Args:
        dry_run: If True, only list the contacts without making changes.
    """
    creds = get_credentials()
    service = build('people', 'v1', credentials=creds)
    
    print("Fetching all contacts (this may take a while)...")
    connections = get_all_contacts(service)
    total_contacts = len(connections)
    print(f"Found {total_contacts} total contacts")
    
    january_first_contacts = []
    
    print("\nScanning for January 1st birthdays...")
    for i, person in enumerate(connections, 1):
        birthdays = person.get('birthdays', [])
        for birthday in birthdays:
            date = birthday.get('date', {})
            if date.get('month') == 1 and date.get('day') == 1:
                name = person.get('names', [{}])[0].get('displayName', 'Unknown')
                january_first_contacts.append((person, name))
                print(f"Found January 1st birthday for: {name}")
        if i % 100 == 0:  # Show progress every 100 contacts
            print(f"Progress: {i}/{total_contacts} contacts checked ({(i/total_contacts)*100:.1f}%)")
    
    if not january_first_contacts:
        print("No contacts found with January 1st birthdays.")
        return
    
    if dry_run:
        print("\nThis was a dry run. No changes were made.")
        print(f"Found {len(january_first_contacts)} contacts with January 1st birthdays.")
        return
    
    # If not dry run, proceed with removing birthdays
    total_to_update = len(january_first_contacts)
    print(f"\nProceeding to remove January 1st birthdays from {total_to_update} contacts...")
    print("This may take a few minutes. Please be patient...")
    
    successful_updates = 0
    failed_updates = 0
    
    for i, (person, name) in enumerate(january_first_contacts, 1):
        birthdays = person.get('birthdays', [])
        for birthday in birthdays:
            date = birthday.get('date', {})
            if date.get('month') == 1 and date.get('day') == 1:
                # Remove the birthday
                birthday['date'] = None
                # Update the contact with etag
                update_body = {
                    'birthdays': birthdays,
                    'metadata': person.get('metadata', {})
                }
                try:
                    print(f"\nUpdating contact {i}/{total_to_update} ({i/total_to_update*100:.1f}%): {name}")
                    service.people().updateContact(
                        resourceName=person['resourceName'],
                        updatePersonFields='birthdays',
                        body=update_body
                    ).execute()
                    print(f"✓ Successfully removed January 1st birthday for {name}")
                    successful_updates += 1
                except Exception as e:
                    print(f"✗ Error updating {name}: {str(e)}")
                    failed_updates += 1
                
                # Add a small delay between updates to make progress visible
                time.sleep(0.5)
    
    print("\nOperation completed!")
    print(f"Summary:")
    print(f"- Total contacts processed: {total_to_update}")
    print(f"- Successful updates: {successful_updates}")
    print(f"- Failed updates: {failed_updates}")

if __name__ == '__main__':
    print("Running in dry-run mode to list contacts with January 1st birthdays...")
    find_january_first_birthdays(dry_run=True)
    
    response = input("\nWould you like to proceed with removing these birthdays? (yes/no): ")
    if response.lower() == 'yes':
        print("\nProceeding with removing January 1st birthdays...")
        find_january_first_birthdays(dry_run=False)
    else:
        print("Operation cancelled.") 