"""TikTok uploader scaffold.

This module provides a minimal scaffold for uploading videos to TikTok.
When no video path is given, downloads a random video from the same Google Drive
folder used for YouTube (DRIVE_FOLDER_ID, googledrive_credentials.json).

Important:
- Prefer using TikTok Content Publishing API (official) — requires a TikTok for Developers app
  and an approved Content Publishing scope (typically requires a Business account and app review).
- Replace placeholders below with your app credentials and an OAuth access token.
"""
import os
import sys
import requests
from typing import Optional, Dict


def download_random_video_from_drive() -> Optional[str]:
    """Download a random video from the Drive folder (same logic as youtube_uploader). Returns local path or None."""
    folder_id = os.environ.get("DRIVE_FOLDER_ID")
    if not folder_id:
        return None
    try:
        from youtube_uploader import authenticate_drive, fetch_random_video_from_drive
    except ImportError:
        return None
    try:
        drive = authenticate_drive()
        video_file_obj = fetch_random_video_from_drive(drive, folder_id)
        if not video_file_obj:
            return None
        return video_file_obj["name"]
    except Exception:
        return None


def upload_video_via_content_api(video_path: str, title: str, access_token: str, extra: Optional[Dict] = None) -> Dict:
    """Upload a video to TikTok using the Content Publishing API (scaffold).

    Args:
        video_path: local path to the video file (mp4/vertical recommended)
        title: caption/title to use for the post
        access_token: OAuth access token with appropriate publish scope
        extra: optional dict for additional parameters (e.g., visibility)

    Returns:
        Parsed JSON response from TikTok (or raises on HTTP error).

    Notes:
    - This is a scaffold. You must replace `api_base` and follow the exact multipart
      upload protocol defined by TikTok's Content API (initiate upload, upload chunks,
      complete upload) — see TikTok developer docs.
    - If you do not have Content Publishing API access, use manual upload or a 3rd-party
      scheduling tool.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"video not found: {video_path}")

    if not access_token:
        raise ValueError("access_token is required for API publishing")

    # Placeholder API base - replace with real endpoint from TikTok docs
    api_base = "https://open-api.tiktok.com"  # confirm in TikTok docs

    # Example: many content APIs require a multipart/form-data POST to an upload URL.
    # This simple single-step upload will probably NOT work for production; it's a starting point.
    url = f"{api_base}/video/upload/?access_token={access_token}"

    with open(video_path, "rb") as f:
        files = {"video_file": (os.path.basename(video_path), f, "video/mp4")}
        data = {"title": title}
        if extra:
            data.update(extra)

        resp = requests.post(url, files=files, data=data, timeout=120)

    resp.raise_for_status()
    return resp.json()


def get_access_token(credentials_file: str = "tiktok_credentials.json") -> str:
    """Get a valid access token by loading credentials and refreshing."""
    from credentials_manager import get_tiktok_access_token
    return get_tiktok_access_token(credentials_file)


def upload_from_config(video_path: str, title: str, config: Optional[Dict] = None) -> Dict:
    """Helper that gets access_token from credentials file (with refresh) or a provided config dict."""
    if config and "access_token" in config:
        token = config["access_token"]
    else:
        token = get_access_token()
    return upload_video_via_content_api(video_path, title, token, extra=config.get("extra") if config else None)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TikTok uploader: pass title only (video from Drive) or video path + title")
    parser.add_argument("video", nargs="?", help="Path to video file (omit to download a random video from Drive)")
    parser.add_argument("title", nargs="?", help="Post title/caption")
    parser.add_argument("--token", help="TikTok access token (optional; default: use tiktok_credentials.json with auto-refresh)")
    parser.add_argument("--credentials", default="tiktok_credentials.json", help="Path to TikTok credentials JSON")
    args = parser.parse_args()
    # One arg → treat as title and get video from Drive
    if args.title is None and args.video is not None:
        args.title = args.video
        args.video = None
    if not args.title:
        raise SystemExit("Usage: tiktok_uploader.py TITLE   or   tiktok_uploader.py VIDEO_PATH TITLE")

    if args.token:
        token = args.token
    else:
        try:
            token = get_access_token(args.credentials)
        except FileNotFoundError:
            raise SystemExit("TikTok credentials file not found. Set TIKTOK_CREDENTIALS_JSON secret or pass --token.")

    video_path = args.video
    if not video_path:
        video_path = download_random_video_from_drive()
        if not video_path:
            print("No video path given and DRIVE_FOLDER_ID not set or no video in Drive.", file=sys.stderr)
            sys.exit(1)
        print(f"Using video from Drive: {video_path}\n")

    print("Uploading... (scaffold)\n")
    res = upload_video_via_content_api(video_path, args.title, token)
    print(res)
