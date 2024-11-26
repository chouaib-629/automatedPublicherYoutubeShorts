import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Authenticate Google Drive
def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

# Authenticate YouTube
def authenticate_youtube():
    credentials = Credentials.from_authorized_user_file("youtube_token.json", ["https://www.googleapis.com/auth/youtube.upload"])
    return build("youtube", "v3", credentials=credentials)

# Fetch video from Google Drive
def fetch_video_from_drive(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and mimeType contains 'video'"}).GetList()
    if not file_list:
        print("No videos found.")
        return None
    video_file = file_list[0]
    video_file.GetContentFile(video_file["title"])
    return video_file["title"]

# Upload video to YouTube
def upload_to_youtube(youtube, video_file, title="Daily Quran Video"):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "A daily Quran short video.",
                "tags": ["Quran", "Islam", "Short Video"],
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    print(f"Uploaded: {response['id']}")
    os.remove(video_file)  # Delete after upload

if __name__ == "__main__":
    folder_id = "your-google-drive-folder-id"  # Replace with your folder ID
    drive = authenticate_drive()
    youtube = authenticate_youtube()
    
    video_file = fetch_video_from_drive(drive, folder_id)
    if video_file:
        upload_to_youtube(youtube, video_file)