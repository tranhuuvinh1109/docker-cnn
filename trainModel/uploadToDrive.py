from django.conf import settings
import os
import tempfile
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')


def authenticate_with_google_drive(client_secrets_path):
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(client_secrets_path)
    gauth.LocalWebserverAuth()
    return gauth


def upload_to_drive():
    model_file_path = os.path.join('D:/Django/CNN/docker-cnn/model/trained_new1.h5')
    try:
        with open(model_file_path, "rb") as file_to_upload:
            gauth = authenticate_with_google_drive(json_filepath)
            drive = GoogleDrive(gauth)

            # Create a temporary zip file to upload to Google Drive
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip_file:
                temp_zip_file.write(file_to_upload.read())

                # Create a new file on Google Drive and set the content from the uploaded zip file
                file_drive = drive.CreateFile({'title': file_to_upload.name})
                file_drive.SetContentFile(temp_zip_file.name)
                file_drive.Upload()
                file_drive.InsertPermission({
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader'
                })

                file_link = file_drive['alternateLink']
                print("file_link  =>>>>>>>>>",file_link)
                
    except Exception as e:
        print("33333333333 >>> exception")
    finally:
        print("33333333333 >>> finally")