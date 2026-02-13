from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

# Save credentials to file for future use
gauth.SaveCredentialsFile("googledrive_credentials.json")

drive = GoogleDrive(gauth)
print("Authentication successful!")
print("Credentials JSON:")
print(gauth.credentials.to_json())