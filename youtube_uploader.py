import os
from functions import (
    authenticate_drive,
    authenticate_youtube,
    fetch_random_video_from_drive,
    get_drive_folder_id,
    dynamic_title_from_video,
    dynamic_description_from_video,
    dynamic_tags_from_video,
)
from googleapiclient.http import MediaFileUpload


def upload_to_youtube(youtube, video_file, title, description, tags):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "27",
            },
            "status": {
                "privacyStatus": "public",
                "comments": "on",
                "license": "youtube",
                "publicStatsViewable": True,
                "selfDeclaredMadeForKids": False,
                "defaultLanguage": "ar",
                "defaultAudioLanguage": "ar",
                "notifySubscribers": True,
            },
        },
        media_body=MediaFileUpload(video_file),
    )
    response = request.execute()
    print(f"Uploaded: {response['id']}")
    return response["id"]


if __name__ == "__main__":
    folder_id = get_drive_folder_id()
    drive = authenticate_drive()
    youtube = authenticate_youtube()

    video_file_obj = fetch_random_video_from_drive(drive, folder_id)
    if video_file_obj:
        video_path = video_file_obj["name"]
        title = dynamic_title_from_video(video_path)
        description = dynamic_description_from_video(video_path)
        tags = dynamic_tags_from_video(video_path)

        video_id = upload_to_youtube(youtube, video_path, title, description, tags)

        playlist_id = os.environ.get("YOUTUBE_PLAYLIST_ID")
        if playlist_id:
            try:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {"kind": "youtube#video", "videoId": video_id},
                        }
                    },
                ).execute()
                print(f"Added to playlist: {playlist_id}")
            except Exception as e:
                print(f"Failed to add to playlist: {e}")

        os.remove(video_path)
