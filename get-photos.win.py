import os
import io
import json
import datetime
import requests
import argparse
import sys

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Set up the API client
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
CLIENT_SECRET_FILE = 'C:\\Users\\istra\\secrets\\client_secret.json'  # Update with correct path
TOKEN_FILE = 'C:\\Users\\istra\\secrets\\token.json'
DATE_TIME_FILE = 'C:\\Users\\istra\\secrets\\last_backup_time.txt' 
DOWNLOAD_FOLDER = 'C:\\Users\\istra\\Documents\\google_photos_download'

# command line parameters
# output file name
# create new token
# start date
# end date


def line_arguments():
    parser = argparse.ArgumentParser(description="Process command line arguments.")

    parser.add_argument("--default", type=str, help="If run without arguments takes defaults from the code.")
    parser.add_argument("--token_file","-t", type=str, help="Path to the token file.")
    parser.add_argument("--start_date","-s",  type=str, help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end_date", "-e", type=str, help="End date (YYYY-MM-DD).")
    parser.add_argument("--download_folder","-d", type=str, help="Folder to store images.")
    parser.add_argument("h", nargs="?", help="Display help message.", default=None)

    args = parser.parse_args()

    # If 'h' is provided, show help and exit
    if args.h is not None:
        parser.print_help()
        sys.exit(0)

    #print(f"Token File: {args.token_file}")
    #print(f"Start Date: {args.start_date}")
    #print(f"End Date: {args.end_date}")
    #print(f"Download folder: {args.download_folder}")
    args = parser.parse_args()
    return(args)


#
#
#



def authenticate(tok_file):
    """Authenticate and return the API client."""
    creds = None
    if not tok_file:
        tok_file = TOKEN_FILE

    print(f"Using token file {tok_file}")

    # Load existing credentials
    if os.path.exists(tok_file):
        creds = Credentials.from_authorized_user_file(tok_file, scopes=["https://www.googleapis.com/auth/photoslibrary.readonly"])

    # If no valid credentials, re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next use
        with open(tok_file, 'w') as token:
            token.write(creds.to_json())

    return build('photoslibrary', 'v1', credentials=creds, discoveryServiceUrl="https://photoslibrary.googleapis.com/$discovery/rest?version=v1")

def list_media_items(service, start_date, end_date):
    """List media items within the specified date range."""
    body = {
        'pageSize': 100,
        'filters': {
            'dateFilter': {
                'ranges': [
                    {
                        'startDate': {
                            'year': start_date.year,
                            'month': start_date.month,
                            'day': start_date.day
                        },
                        'endDate': {
                            'year': end_date.year,
                            'month': end_date.month,
                            'day': end_date.day
                        }
                    }
                ]
            }
        }
    }

    results = service.mediaItems().search(body=body).execute()
    return results.get('mediaItems', [])

def download_media(media_item, download_folder):
    """Download a media item using the correct method."""
    filename = media_item['filename']

    mime_type = media_item['mimeType']

    if 'image' in mime_type:
        file_url = media_item['baseUrl'] + '=d'  # Download highest quality image
    elif 'video' in mime_type:
        file_url = media_item['baseUrl'] + '=dv'  # Use '=dv' for high-quality video download
    else:
        print("Unknown media type")
        exit()


    # obsolete file_url = media_item['baseUrl'] + '=dv'  # Append '=d' to get the download URL
    save_path = os.path.join(download_folder, filename)

    response = requests.get(file_url, stream=True)  # Use requests to download
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

# def get_dates()
# Read the last backup date from file, set current time
#
#


def write_datetime_to_file(filename,date_time):
    date_time_formatted=date_time.strftime("%Y-%m-%d %H:%M:%S")
    # Write to file
    with open(filename, "w") as file:
        file.write(date_time_formatted)
    print(f"Current date and time written to {filename}")

def read_datetime_from_file(filename):
    try:
        with open(filename, "r") as file:
            content = file.read()
            print(f"End date read from file {filename} and set to {content}")
            return content
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

#
#
#

def main():
    """Main function to authenticate and download photos."""
    #get command line arguments
    args = line_arguments()
    
    service = authenticate(args.token_file)
    if args.download_folder:
        download_folder = args.download_folder
    else:
        download_folder = DOWNLOAD_FOLDER
    os.makedirs(download_folder, exist_ok=True)
    if os.path.exists(download_folder):
        print(f"Folder {download_folder} ready to accept files.")
    else:
        print(f"Failed to create folder {download_folder}")
        sys.exit(255)
    
    current_datetime = datetime.datetime.now()
#
#  start_date = datetime.date(2025, 1, 1)  # Replace with your start date
#
#    end_date = datetime.date(2025, 1, 3)  # Replace with your end date
#
    if args.start_date:
        start_date = datetime.datetime.strptime(args.start_date,"%Y-%m-%d" )
    else:
        start_date = datetime.datetime.strptime(read_datetime_from_file(DATE_TIME_FILE),"%Y-%m-%d %H:%M:%S" )

    if start_date:
        if args.end_date:
            end_date = datetime.datetime.strptime(args.end_date,"%Y-%m-%d" )
        else:
            end_date = current_datetime

        media_items = list_media_items(service, start_date, end_date)

        if not media_items:
            print('No media items found.')
        else:
            for media_item in media_items:
                download_media(media_item, download_folder)
        write_datetime_to_file(DATE_TIME_FILE,end_date)
    else:
        print(f"Can not read date from file {DATE_TIME_FILE}")
    

if __name__ == '__main__':
    main()