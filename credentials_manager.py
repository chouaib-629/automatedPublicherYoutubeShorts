import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def load_and_refresh_youtube_credentials(credentials_file="youtube_credentials.json"):
    """
    Load YouTube credentials from file and automatically refresh if expired.
    On first run, use youtubeCredentials_test.py to generate youtube_credentials.json
    """
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"{credentials_file} not found. Run youtubeCredentials_test.py first to generate it."
        )
    
    # Load credentials from file
    with open(credentials_file, 'r') as f:
        creds_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(
        creds_data,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    
    # Refresh if expired
    if creds.expired and creds.refresh_token:
        print("Refreshing YouTube credentials...")
        creds.refresh(Request())
        
        # Save the refreshed credentials back to file
        with open(credentials_file, 'w') as f:
            f.write(creds.to_json())
        print("YouTube credentials refreshed and saved.")
    
    return creds

def get_youtube_service(credentials_file="youtube_credentials.json"):
    """Get authenticated YouTube service"""
    creds = load_and_refresh_youtube_credentials(credentials_file)
    return build("youtube", "v3", credentials=creds)

def load_and_refresh_drive_credentials(credentials_file="googledrive_credentials.json"):
    """
    Load Google Drive credentials from file and automatically refresh if expired.
    On first run, use driveCredentials_test.py to generate googledrive_credentials.json
    """
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"{credentials_file} not found. Run driveCredentials_test.py first to generate it."
        )
    
    # Load credentials from file
    with open(credentials_file, 'r') as f:
        creds_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(
        creds_data,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    
    # Refresh if expired
    if creds.expired and creds.refresh_token:
        print("Refreshing Drive credentials...")
        creds.refresh(Request())
        
        # Save the refreshed credentials back to file
        with open(credentials_file, 'w') as f:
            f.write(creds.to_json())
        print("Drive credentials refreshed and saved.")
    
    return creds

def get_drive_service(credentials_file="googledrive_credentials.json"):
    """Get authenticated Google Drive service using Google API Client"""
    creds = load_and_refresh_drive_credentials(credentials_file)
    return build("drive", "v3", credentials=creds)
    gauth = load_and_refresh_drive_credentials(settings_yaml, credentials_file)
    return GoogleDrive(gauth)
