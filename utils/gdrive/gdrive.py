from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv
from utils.cypher.key import get_api_key, ENV_FILE
import os
import io
import json

load_dotenv(ENV_FILE, override=True)

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'creds.json'
PARENT_FOLDER_ID = get_api_key("GDRIVE_FOLDER_ID")


def authenticate():
    """Authenticate and return credentials."""
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds


def create_folder(service, folder_name, parent_id):
    """Create a folder if it doesn't exist and return its ID."""
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f"Created folder '{folder_name}' with ID: {folder.get('id')}")
    return folder.get('id')


def find_file(service, file_name, folder_id):
    """Search for a file in a specific folder by name."""
    query = f"name = '{file_name}' and '{folder_id}' in parents"
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = results.get('files', [])
    return files[0] if files else None


def append_to_file(service, file_id, new_content):
    """Download file content, append new content, and re-upload."""
    request = service.files().get_media(fileId=file_id)
    file_content = io.BytesIO()
    downloader = MediaIoBaseDownload(file_content, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    # Append new content
    file_content.seek(0)
    current_content = file_content.read().decode()
    updated_content = current_content + "\n" + new_content

    # Re-upload file
    media = MediaFileUpload(io.BytesIO(updated_content.encode()), mimetype='text/plain')
    service.files().update(fileId=file_id, media_body=media).execute()
    print("Appended content to file.")


def upload_or_append(file_path, file_name, destination_name=None):
    """Main logic to upload or append content to a file."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Find or create the destination folder
    folder_id = PARENT_FOLDER_ID
    if destination_name:
        query = f"name = '{destination_name}' and mimeType = 'application/vnd.google-apps.folder'"
        results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
        folder = results.get('files', [])
        if not folder:
            folder_id = create_folder(service, destination_name, PARENT_FOLDER_ID)
        else:
            folder_id = folder[0]['id']

    # Find the file in the folder
    file = find_file(service, file_name, folder_id)
    if file:
        print(f"File '{file_name}' exists. Appending content.")
        append_to_file(service, file['id'], open(file_path, 'r').read())
    else:
        print(f"File '{file_name}' not found. Uploading a new file.")
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        service.files().create(body=file_metadata, media_body=media).execute()
        print(f"Uploaded file '{file_name}' to folder '{destination_name or PARENT_FOLDER_ID}'.")


# Example usage
# upload_or_append("llm.py", "llm.py", "MyDestinationFolder")
upload_or_append("llm.py", "llm.py")
