# TikTok OAuth callback

Local callback server so TikTok can redirect to a public URL and you can copy the **authorization code**. Use this code once to exchange it for an access token and refresh token, then store them in `tiktok_credentials.json` for the main project.

## Structure

- **`index.php`** — Callback at the root: `https://YOUR-NGROK-URL/`
- **`callback/index.php`** — Callback at path: `https://YOUR-NGROK-URL/callback`

Both pages read `?code=...` from the URL and display it so you can copy it. The code is single-use.

## Prerequisites

- PHP (built-in web server)
- [ngrok](https://ngrok.com/) (or similar) to expose localhost over HTTPS

## Run the server

From the **project root** (or from `tiktok-oauth`):

```bash
cd tiktok-oauth
php -S localhost:9090
```

In another terminal, expose it with ngrok:

```bash
ngrok http 9090
```

Use the ngrok **HTTPS** URL (e.g. `https://xxxx.ngrok-free.app`) as your TikTok app’s **Redirect URI**.

## Redirect URI options

In the [TikTok Developer Portal](https://developers.tiktok.com/), add one of these as a redirect URI for your app:

| Option | Redirect URI | Authorize URL |
|--------|--------------|---------------|
| **Root** | `https://YOUR-NGROK-URL/` | Use this exact URL, URL-encoded in the authorize link |
| **Path** | `https://YOUR-NGROK-URL/callback` | Same: add in app, use encoded in authorize URL |

After you authorize in TikTok, you’ll be redirected to this page and the code will be shown. Copy it and use it **once** to call TikTok’s token endpoint and get `access_token` and `refresh_token`. Save `refresh_token` (and `client_key`, `client_secret`) in `tiktok_credentials.json` so the main project can refresh tokens for uploads.
