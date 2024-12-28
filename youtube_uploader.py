import os
import random
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Authenticate Google Drive using environment variables or file
def authenticate_drive():
    # Load the credentials from the environment variable or GitHub Secrets
    with open("client_secrets.json", "w") as f:
        f.write(os.environ["GOOGLE_DRIVE_CREDENTIALS"])
    
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile("client_secrets.json")
    gauth.Authorize()
    return GoogleDrive(gauth)

# Authenticate YouTube using environment variables or file
def authenticate_youtube():
    with open("client_secrets_youtube.json", "w") as f:
        f.write(os.environ["YOUTUBE_CREDENTIALS"])

    credentials = Credentials.from_authorized_user_file("client_secrets_youtube.json", ["https://www.googleapis.com/auth/youtube.upload"])
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