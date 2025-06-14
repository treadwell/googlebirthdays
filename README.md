# Google Contacts Birthday Cleanup

This script removes January 1st birthdays from your Google Contacts using the Google People API.

## Setup

1. First, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up Google Cloud Project and enable the People API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google People API for your project
   - Go to the Credentials page
   - Create an OAuth 2.0 Client ID
   - Download the client configuration file and save it as `credentials.json` in the same directory as the script

## Usage

1. Run the script:
   ```bash
   python cleanup_birthdays.py
   ```

2. The first time you run the script, it will:
   - Open your default web browser
   - Ask you to log in to your Google account
   - Request permission to access your contacts
   - Save the authentication token for future use

3. The script will then:
   - Fetch all your contacts
   - Remove any January 1st birthdays
   - Print the names of contacts that were updated

## Security Note

The script creates a `token.pickle` file to store your authentication credentials. Keep this file secure and don't share it with others. 