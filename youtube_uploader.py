import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Authenticate Google Drive using credentials loaded directly from environment variables
def authenticate_drive():
    google_drive_credentials = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
    if not google_drive_credentials:
        raise ValueError("Google Drive credentials not found in environment variables.")
    
    # Load the credentials as a JSON object and pass it to PyDrive
    client_config = json.loads(google_drive_credentials)
    
    gauth = GoogleAuth()
    gauth.credentials = client_config  # Directly assign the credentials
    gauth.Authorize()
    return GoogleDrive(gauth)

# Authenticate YouTube using credentials loaded directly from environment variables
def authenticate_youtube():
    youtube_credentials = os.environ.get("YOUTUBE_CREDENTIALS")
    if not youtube_credentials:
        raise ValueError("YouTube credentials not found in environment variables.")
    
    # Load the credentials as a JSON object
    credentials_info = json.loads(youtube_credentials)
    
    # Create credentials object directly from the loaded JSON data
    credentials = Credentials.from_authorized_user_info(credentials_info, ["https://www.googleapis.com/auth/youtube.upload"])
    
    return build("youtube", "v3", credentials=credentials)

# Fetch a random video from Google Drive
def fetch_random_video_from_drive(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and mimeType contains 'video'"}).GetList()
    if not file_list:
        print("No videos found.")
        return None
    video_file = random.choice(file_list)
    video_file.GetContentFile(video_file["title"])  # Download the video file locally
    return video_file["title"]

# Upload video to YouTube
def upload_to_youtube(youtube, video_file, title="صلو على النبي محمد 💚💚"):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "صلو على النبي محمد 💚💚. A daily Quran short video.",
                "tags": ["quran", "quranrecitation", "راحة نفسية"],
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": "public",
                "comments": "on",  
                "license": "youtube",
                "publicStatsViewable": True,
                "selfDeclaredMadeForKids": False,
                "defaultLanguage": "ar",
                "defaultAudioLanguage": "ar",
                "notifySubscribers": True
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    print(f"Uploaded: {response['id']}")

if __name__ == "__main__":
    folder_id = "1On3DP-7IHF3U_Doc-hWha5q3xYpoP2i9"  # Replace with your folder ID
    drive = authenticate_drive()
    youtube = authenticate_youtube()
    
    video_file = fetch_random_video_from_drive(drive, folder_id)
    if video_file:
        from datetime import datetime
        title = f"صلو على النبي محمد 💚💚 - {datetime.now().strftime('%Y-%m-%d')}"
        upload_to_youtube(youtube, video_file, title)