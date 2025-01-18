GPT and I played on the theme of getting Google Photos. Storing the Python. Have fun according to GPL 3.

Prerequisites
1. Create a Google Cloud Project
2. Enable Google Photo APIs
3. Create an OAuth Authentication

Usage:
Run

 python .\get-photos.v2.py -h

 Follow the instructions below:

usage: get-photos.v2.py [-h] [--default DEFAULT] [--token_file TOKEN_FILE] [--start_date START_DATE] [--end_date END_DATE] [--download_folder DOWNLOAD_FOLDER] [h]

Process command line arguments.

positional arguments:
  h                     Display help message.

options:
  -h, --help            show this help message and exit
  --default DEFAULT     If run without arguments takes defaults from the code.
  --token_file TOKEN_FILE, -t TOKEN_FILE
                        Path to the token file.
  --start_date START_DATE, -s START_DATE
                        Start date (YYYY-MM-DD).
  --end_date END_DATE, -e END_DATE
                        End date (YYYY-MM-DD).
  --download_folder DOWNLOAD_FOLDER, -d DOWNLOAD_FOLDER
                        Folder to store images.
