from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ["https://www.googleapis.com/auth/drive"]

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secrets_youtube.json", SCOPES
)
credentials = flow.run_local_server(port=0)

# Save credentials to file for future use
with open("googledrive_credentials.json", "w") as f:
    f.write(credentials.to_json())

print("Authentication successful!")
print("Credentials saved to googledrive_credentials.json")
print("Credentials JSON:")
print(credentials.to_json())