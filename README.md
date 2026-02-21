# Automated Publisher for YouTube Shorts & TikTok

Automatically publish short videos from a **Google Drive folder** to **YouTube Shorts** and **TikTok** on a schedule, using GitHub Actions. No manual uploads—drop videos into Drive and they get published with dynamic titles and metadata.

---

## What this project does

- **Single source of videos**: One Google Drive folder holds your short-form content. Each run picks a **random** video from that folder, so YouTube and TikTok can each get a different video (or the same one, depending on timing).
- **YouTube Shorts**: Uploads to your YouTube channel as a Short, with auto-generated title, description, and tags based on the video filename (e.g. reciter/imam name). Optionally adds the video to a playlist.
- **TikTok**: Publishes via the TikTok Content Posting API—either direct publish or to your TikTok inbox for one-tap posting. Uses the same Drive folder and the same dynamic title logic.
- **Scheduled and manual**: Workflows run daily (e.g. 16:00 UTC) and can also be triggered manually from the Actions tab.

---

## How it works

1. **GitHub Actions** runs on a schedule or when you trigger it.
2. The workflow creates credential files from your GitHub secrets (Google Drive, YouTube, and/or TikTok).
3. The Python script authenticates with Google Drive, lists videos in your folder, and selects one at random.
4. It downloads that video, builds a title (and for YouTube: description and tags) from the filename (e.g. using a known reciter name), then uploads to YouTube and/or TikTok.
5. After upload, the local file is removed. Each platform has its own workflow, so you can run YouTube only, TikTok only, or both on different schedules.

---

## Project structure

| Path | Purpose |
|------|--------|
| `youtube_uploader.py` | YouTube Shorts upload: Drive → random video → upload with dynamic title/description/tags, optional playlist. |
| `tiktok_uploader.py` | TikTok upload: Drive → random video → TikTok Content Posting API (direct or inbox). |
| `functions.py` | Shared logic: Drive auth, random video fetch, folder ID, dynamic title/description/tags from video filename. |
| `credentials_manager.py` | Loads and refreshes OAuth credentials for Google (Drive, YouTube) and TikTok. |
| `.github/workflows/youtube_upload.yml` | Workflow that runs only the YouTube publisher. |
| `.github/workflows/tiktok_upload.yml` | Workflow that runs only the TikTok publisher. |
| `docs/` | GitHub Pages site (Terms of Service, Privacy Policy) for app store / developer portal links. |

---

## Setup

### 1. Clone and use this repo (or fork it)

```bash
git clone https://github.com/chouaib-629/automatedPublicherYoutubeShorts.git
cd automatedPublicherYoutubeShorts
```

### 2. Dependencies

```bash
pip install -r requirements.txt
```

### 3. GitHub Actions secrets

Configure these in your repo: **Settings → Secrets and variables → Actions**.

| Secret | Used by | Description |
|--------|---------|-------------|
| `GOOGLEDRIVE_CREDENTIALS_JSON` | YouTube & TikTok workflows | Full JSON of your Google Drive OAuth credentials (so the runner can read the video folder). |
| `DRIVE_FOLDER_ID` | Both | The Google Drive folder ID that contains your short videos. |
| `YOUTUBE_CREDENTIALS_JSON` | YouTube workflow only | Full JSON of your YouTube OAuth credentials. |
| `YOUTUBE_PLAYLIST_ID` | YouTube workflow only | (Optional) Add each uploaded Short to this playlist. |
| `TIKTOK_CREDENTIALS_JSON` | TikTok workflow only | JSON with `refresh_token`, `client_key`, `client_secret` (and optionally `access_token`). Used for token refresh and uploads. |

The workflows write these into `googledrive_credentials.json`, `youtube_credentials.json`, and `tiktok_credentials.json` at run time; the scripts read from those files.

### 4. Schedules and manual runs

- **Schedules** are defined in each workflow file (e.g. `cron: "0 16 * * *"` = daily at 16:00 UTC). Edit the `on.schedule` in `.github/workflows/youtube_upload.yml` and `tiktok_upload.yml` to change them.
- **Manual run**: In GitHub, go to **Actions**, select “Publish to YouTube” or “Publish to TikTok”, and click **Run workflow**.

---

## Dynamic titles and metadata

Titles (and for YouTube, description and tags) are built from the **video filename**:

- If the filename starts with a known reciter name (e.g. from a list in `functions.py`), that name is included in the title and tags.
- A standard phrase and date are added (e.g. “صلو على النبي محمد …” and the current date).
- Hashtags and tags are applied so both platforms get consistent, relevant metadata.

You can change the list of names and the title/description templates in `functions.py`.

---

## Legal and links

- [Terms of Service](TERMS_OF_SERVICE.md)
- [Privacy Policy](PRIVACY_POLICY.md)

Website (GitHub Pages): [https://chouaib-629.github.io/automatedPublicherYoutubeShorts/](https://chouaib-629.github.io/automatedPublicherYoutubeShorts/)

### TikTok app review: "This URL is not verified"

TikTok requires **URL verification** before the Web, Terms, and Privacy URLs are accepted. You must use the **URL properties** flow and add TikTok’s signature file to this site:

1. In [TikTok for Developers](https://developers.tiktok.com/) → your app → click **URL properties** (top of the app page).
2. Choose **Verify by URL prefix** and enter: `https://chouaib-629.github.io/automatedPublicherYoutubeShorts/`
3. Download the **signature file** TikTok provides, add it to the **`docs/`** folder, then commit and push.
4. Complete verification in the portal. After that, use the GitHub Pages URLs above for Web, Terms, and Privacy in App details.

See **`docs/README.md`** for step-by-step instructions.

---

## License and disclaimer

This project is provided as-is. You are responsible for complying with YouTube’s and TikTok’s terms, community guidelines, and any applicable laws. Keep credentials and tokens secure and never commit them to the repo.
