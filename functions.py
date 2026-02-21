"""Shared functions for YouTube and TikTok uploaders.

Both youtube_uploader.py and tiktok_uploader.py depend on this module. Unified here:
- Drive: get_drive_folder_id, authenticate_drive, fetch_random_video_from_drive, download_random_video_from_drive, DEFAULT_DRIVE_FOLDER_ID
- YouTube auth: authenticate_youtube
- Title/description/tags: parse_imam_from_video_name, dynamic_title_from_video, dynamic_description_from_video, dynamic_tags_from_video (IMAMS list)
"""
import os
import random
import io
from datetime import datetime
from typing import Optional

from credentials_manager import get_youtube_service, get_drive_service
from googleapiclient.http import MediaIoBaseDownload


# Imams list for parsing video filenames and building titles
IMAMS = ["الشيخ ماهر المعيقلي", "القارئ إسلام صبحي", "الشيخ ياسر الدوسري"]

# Default Drive folder when DRIVE_FOLDER_ID env is not set (shared by YouTube and TikTok flows)
DEFAULT_DRIVE_FOLDER_ID = "1On3DP-7IHF3U_Doc-hWha5q3xYpoP2i9"


def get_drive_folder_id() -> str:
    """Return DRIVE_FOLDER_ID env or DEFAULT_DRIVE_FOLDER_ID (single place for resolution)."""
    return os.environ.get("DRIVE_FOLDER_ID", DEFAULT_DRIVE_FOLDER_ID)


def authenticate_drive():
    try:
        return get_drive_service()
    except FileNotFoundError as e:
        raise ValueError(f"Drive credentials error: {str(e)}")


def authenticate_youtube():
    try:
        return get_youtube_service()
    except FileNotFoundError as e:
        raise ValueError(f"YouTube credentials error: {str(e)}")


def fetch_random_video_from_drive(drive_service, folder_id: str):
    """Fetch a random video from Google Drive folder; download to cwd. Returns video_file dict or None."""
    query = f"'{folder_id}' in parents and mimeType contains 'video'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        print("No videos found.")
        return None
    video_file = random.choice(files)
    request = drive_service.files().get_media(fileId=video_file["id"])
    with io.FileIO(video_file["name"], "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    return video_file


def download_random_video_from_drive() -> Optional[str]:
    """Download a random video from Drive (DRIVE_FOLDER_ID env, or DEFAULT_DRIVE_FOLDER_ID). Returns local path or None."""
    folder_id = get_drive_folder_id()
    if not folder_id:
        return None
    try:
        drive = authenticate_drive()
        video_file_obj = fetch_random_video_from_drive(drive, folder_id)
        if not video_file_obj:
            return None
        return video_file_obj["name"]
    except Exception:
        return None


def parse_imam_from_video_name(video_title: str) -> Optional[str]:
    """Return imam name if video_title starts with one of IMAMS, else None."""
    for imam in IMAMS:
        if video_title.startswith(imam):
            return imam
    return None


def dynamic_title_from_video(video_path: str) -> str:
    """Build title from video filename: imam + date + hashtags (same for YouTube and TikTok)."""
    video_title = os.path.basename(video_path)
    imam = parse_imam_from_video_name(video_title)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    if imam:
        return f"{imam} - صلو على النبي محمد 💚💚 #راحة_نفسية #quran #quranrecitation - {date_str}"
    return f"صلو على النبي محمد 💚💚 #راحة_نفسية #quran #quranrecitation - {date_str}"


def dynamic_description_from_video(video_path: str) -> str:
    """Build YouTube description from video filename."""
    video_title = os.path.basename(video_path)
    imam = parse_imam_from_video_name(video_title)
    base_desc = "صلو على النبي محمد 💚💚. فيديو قرآني قصير يومي."
    if imam:
        return f"{base_desc} تلاوة من {imam}. استمع إلى القرآن الكريم واطمئن روحك. #قرآن #تلاوة #{imam.replace(' ', '')} #راحة_نفسية #quran #quranrecitation #إسلام"
    return f"{base_desc} استمع إلى القرآن الكريم واطمئن روحك. #قرآن #تلاوة #راحة_نفسية #quran #quranrecitation #إسلام"


def dynamic_tags_from_video(video_path: str) -> list:
    """Build YouTube tags list from video filename."""
    video_title = os.path.basename(video_path)
    imam = parse_imam_from_video_name(video_title)
    base_tags = ["قرآن", "تلاوة", "قرآن كريم", "إسلام", "راحة نفسية", "قرآن يومي", "تلاوة قرآن", "سورة", "آية", "محمد", "نبي"]
    if imam:
        return base_tags + [imam, imam.replace(" ", "_")]
    return base_tags
