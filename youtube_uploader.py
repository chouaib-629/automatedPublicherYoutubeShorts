import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials
import random
from datetime import datetime

# Authenticate Google Drive using credentials loaded directly from environment variables
def authenticate_drive():
    google_drive_credentials = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
    if not google_drive_credentials:
        raise ValueError("Google Drive credentials not found in environment variables.")
    
    # Load the credentials using oauth2client (required for PyDrive)
    credentials = OAuth2Credentials.from_json(google_drive_credentials)
    
    # Set up PyDrive authentication directly with loaded credentials
    gauth = GoogleAuth()
    gauth.credentials = credentials
    gauth._client = None  # Ensure that no file-based client is used
    gauth._loaded = True  # Mark that credentials have been loaded
    drive = GoogleDrive(gauth)  # Create GoogleDrive object
    return drive

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
    return video_file

# Upload video to YouTube
def upload_to_youtube(youtube, video_file, title, description, tags):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "27",  # Education category for Quran content
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
    return response['id']

if __name__ == "__main__":
    # List of imams for parsing
    imams = ["الشيخ ماهر المعيقلي", "القارئ إسلام صبحي", "الشيخ ياسر الدوسري"]
    
    folder_id = os.environ.get("DRIVE_FOLDER_ID", "1On3DP-7IHF3U_Doc-hWha5q3xYpoP2i9")  # Use env var or default
    drive = authenticate_drive()
    youtube = authenticate_youtube()
    
    video_file_obj = fetch_random_video_from_drive(drive, folder_id)
    if video_file_obj:
        video_title = video_file_obj["title"]
        video_path = video_file_obj["title"]
        
        # Parse imam from video title
        imam = None
        for i in imams:
            if video_title.startswith(i):
                imam = i
                break
        
        # Set dynamic title
        date_str = datetime.now().strftime('%Y-%m-%d')
        if imam:
            title = f"{imam} - صلو على النبي محمد 💚💚 #راحة_نفسية #quran #quranrecitation - {date_str}"
        else:
            title = f"صلو على النبي محمد 💚💚 #راحة_نفسية #quran #quranrecitation - {date_str}"
        
        # Set dynamic description
        base_desc = "صلو على النبي محمد 💚💚. فيديو قرآني قصير يومي."
        if imam:
            description = f"{base_desc} تلاوة من {imam}. استمع إلى القرآن الكريم واطمئن روحك. #قرآن #تلاوة #{imam.replace(' ', '')} #راحة_نفسية #quran #quranrecitation #إسلام"
        else:
            description = f"{base_desc} استمع إلى القرآن الكريم واطمئن روحك. #قرآن #تلاوة #راحة_نفسية #quran #quranrecitation #إسلام"
        
        # Set dynamic tags
        base_tags = ["قرآن", "تلاوة", "قرآن كريم", "إسلام", "راحة نفسية", "قرآن يومي", "تلاوة قرآن", "سورة", "آية", "محمد", "نبي"]
        if imam:
            tags = base_tags + [imam, imam.replace(" ", "_")]
        else:
            tags = base_tags
        
        video_id = upload_to_youtube(youtube, video_path, title, description, tags)
        
        # Optional: Add to playlist if PLAYLIST_ID is set
        playlist_id = os.environ.get("YOUTUBE_PLAYLIST_ID")
        if playlist_id:
            try:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                ).execute()
                print(f"Added to playlist: {playlist_id}")
            except Exception as e:
                print(f"Failed to add to playlist: {e}")
        
        os.remove(video_path)  # Clean up the downloaded file