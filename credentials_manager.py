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

def get_tiktok_access_token(credentials_file="tiktok_credentials.json"):
    """
    Load TikTok credentials from file (refresh_token, client_key, client_secret),
    refresh to get a new access_token, and return it.
    TIKTOK_CREDENTIALS_JSON should contain: refresh_token, client_key, client_secret.
    """
    import urllib.request
    import urllib.parse
    import urllib.error

    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"{credentials_file} not found. Set TIKTOK_CREDENTIALS_JSON secret and create the file in the workflow."
        )

    with open(credentials_file, "r") as f:
        data = json.load(f)

    refresh_token = data.get("refresh_token")
    client_key = data.get("client_key") or os.environ.get("TIKTOK_CLIENT_KEY")
    client_secret = data.get("client_secret") or os.environ.get("TIKTOK_CLIENT_SECRET")

    missing = []
    if not refresh_token:
        missing.append("refresh_token")
    if not client_key:
        missing.append("client_key")
    if not client_secret:
        missing.append("client_secret")
    if missing:
        raise ValueError(
            "TIKTOK_CREDENTIALS_JSON is missing: %s. "
            "Add them to the same JSON: client_key and client_secret are in TikTok Developer Portal (your app); "
            "refresh_token is in the token response you already have."
            % ", ".join(missing)
        )

    body = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise ValueError("TikTok token refresh failed (%s): %s" % (e.code, body))

    if "access_token" not in result:
        raise ValueError("TikTok token refresh failed: %s" % result)

    return result["access_token"]
