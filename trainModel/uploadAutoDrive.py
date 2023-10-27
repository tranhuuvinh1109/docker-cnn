from rest_framework.views import APIView
from rest_framework.response import Response
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload


class uploadAuto:
    def Upload_auto_drive(file_path, file_name):
        print(">>>DANG UP NE>>>>")
        SERVICE_ACCOUNT_FILE = 'F:/WORKS/MATERIALS/4th_year/LapTrinhMang/docker-cnn/client_secrets.json'
        SCOPES = ['https://www.googleapis.com/auth/drive.file']

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        drive_service = build('drive', 'v3', credentials=credentials)


        folder_id = '1aAIkfZS-anf5E6M8uj5nUka5B8Iy4yQn'

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        if 'id' in file:
            file_id = file['id']
            file_url = "https://drive.google.com/file/d/" + file_id + "/view"
            # https://drive.google.com/file/d/15aZezP89eENIpUh5pQ-HjivtWXOj0uY_/view

            return file_url
        else:
            return 0