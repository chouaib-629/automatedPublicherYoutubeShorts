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


API_BASE = "https://open.tiktokapis.com"


def _query_creator_info(access_token: str) -> Dict:
    """Get creator info including privacy_level_options (required for init)."""
    resp = requests.post(
        f"{API_BASE}/v2/post/publish/creator_info/query/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("error", {}).get("code") != "ok":
        raise ValueError("Creator info query failed: %s" % data)
    return data


def _init_video_upload(
    access_token: str,
    title: str,
    video_size: int,
    privacy_level: str = "SELF_ONLY",
) -> str:
    """Initialize direct post; returns upload_url."""
    # Single chunk: whole file
    chunk_size = video_size
    total_chunk_count = 1
    body = {
        "post_info": {
            "title": title[:2200] if title else "",
            "privacy_level": privacy_level,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunk_count,
        },
    }
    resp = requests.post(
        f"{API_BASE}/v2/post/publish/video/init/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json=body,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("error", {}).get("code") != "ok":
        raise ValueError("Init failed: %s" % data.get("error", data))
    upload_url = (data.get("data") or {}).get("upload_url")
    if not upload_url:
        raise ValueError("No upload_url in response: %s" % data)
    return upload_url


def _put_video(upload_url: str, video_path: str) -> None:
    """Upload video binary to TikTok upload_url."""
    size = os.path.getsize(video_path)
    headers = {
        "Content-Type": "video/mp4",
        "Content-Length": str(size),
        "Content-Range": f"bytes 0-{size - 1}/{size}",
    }
    with open(video_path, "rb") as f:
        resp = requests.put(upload_url, data=f, headers=headers, timeout=120)
    resp.raise_for_status()


def upload_video_via_content_api(video_path: str, title: str, access_token: str, extra: Optional[Dict] = None) -> Dict:
    """Upload a video to TikTok using the Content Posting API (Direct Post).

    1. Query creator info for privacy_level_options.
    2. Initialize post (get upload_url).
    3. PUT video to upload_url.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"video not found: {video_path}")

    if not access_token:
        raise ValueError("access_token is required for API publishing")

    # Step 1: creator info (required for valid privacy_level)
    creator = _query_creator_info(access_token)
    options = (creator.get("data") or {}).get("privacy_level_options") or []
    privacy_level = options[0] if options else "SELF_ONLY"

    # Step 2: init
    video_size = os.path.getsize(video_path)
    upload_url = _init_video_upload(access_token, title, video_size, privacy_level)

    # Step 3: upload
    _put_video(upload_url, video_path)

    return {"status": "ok", "message": "Video uploaded; post is processing."}


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

    print("Uploading to TikTok (Content Posting API)...\n")
    res = upload_video_via_content_api(video_path, args.title, token)
    print(res)
