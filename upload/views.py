import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from .sendMail import *
import tempfile

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')
json_filepath1 = os.path.join(base_dir, 'document', 'docker-cnn-google.json')


def authenticate_google_drive(request):
    # Gọi API và nhận URL xác thực từ Google Drive
    # Ví dụ:
    authentication_url = "https://accounts.google.com/o/oauth2/auth..."  # URL xác thực thực sự từ Google Drive

    response_data = {
        'authentication_url': authentication_url
    }

    return JsonResponse(response_data)


# def authenticate_with_google_drive(client_secrets_path):
#     gauth = GoogleAuth()
#     gauth.LoadClientConfigFile(client_secrets_path)
#     gauth.LocalWebserverAuth()
#     return gauth

def authenticate_with_google_drive():
    gauth = GoogleAuth()
    gauth.auth_method = 'service'
    gauth.LoadClientConfigFile(json_filepath1)
    gauth.LocalWebserverAuth()
    return gauth


def success(request):
    return render(request,'upload/upload_success.html')


def upload_folder(path, file_name):
    try:
        gauth = authenticate_with_google_drive()
        drive = GoogleDrive(gauth)

        file_drive = drive.CreateFile({'title': file_name})
        file_drive.SetContentFile(path)
        file_drive.Upload()
        file_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        file_link = file_drive['alternateLink']
        print("file_link  =>>>>>>>>>", file_link)

        sendMailToDrive('tranhuudu113@gmail.com', file_link)
        print("uploaded  =>>>>>>>>>")
        return file_link

    except Exception as e:
        print(e)
