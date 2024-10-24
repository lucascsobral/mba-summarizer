from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Caminho para o arquivo da chave JSON baixado
SERVICE_ACCOUNT_FILE = os.getenv("PATH_CREDENTIAL_GOOGLE")
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")


# Defina o escopo que seu app precisa
SCOPES = ['https://www.googleapis.com/auth/drive']

class GoogleDriveManager:
    def __init__(self, service_account_file: str, scopes: List[str]) -> None:
        # Initialize credentials and Google Drive API service
        self.credentials: Credentials = Credentials.from_service_account_file(
            service_account_file, scopes=scopes)
        self.service = build('drive', 'v3', credentials=self.credentials)

    def list_files_in_folder(self, folder_id: str) -> List[Dict[str, str]]:
        try:
            # List files in a specified folder
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                pageSize=100,  # You can adjust this
                fields="files(id, name)"
            ).execute()
            items = results.get('files', [])

            if not items:
                print('No files found.')
            else:
                print('Files in folder:')
                for item in items:
                    print(f"{item['name']} ({item['id']})")

            return items

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def list_folders_in_folder(self, folder_id: str) -> int:
        try:
            query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name)"
            ).execute()

            folders = results.get('files', [])

            if not folders:
                print('No folders found.')
            else:
                print(f'Found {len(folders)} folders:')
                for folder in folders:
                    print(f"{folder['name']} ({folder['id']})")

            return len(folders)

        except HttpError as error:
            print(f'An error occurred: {error}')
            return 0

    def create_formatted_folder(self, base_name: str, folder_count: int, parent_folder_id: str) -> str | None:
        # Create a folder with formatted name (e.g., "00+folder_name")
        formatted_name = f"{folder_count:02d}-{base_name}"

        folder_metadata = {
            'name': formatted_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }

        try:
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            print(f'Folder "{formatted_name}" created successfully with ID: {folder.get("id")}')
            return folder.get('id')
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def upload_file_to_folder(self, file_name: str, file_path: str, folder_id: str) -> None:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]  # Specify the folder where the file will be uploaded
        }
        media = MediaFileUpload(file_path, resumable=True)

        try:
            # Upload the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            print(f'File "{file_name}" uploaded successfully with ID: {file.get("id")}')
        except HttpError as error:
            print(f'An error occurred: {error}')



