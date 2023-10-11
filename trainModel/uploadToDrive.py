from django.conf import settings
import os
import tempfile
import os
import json
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')
# json_filepath1 = os.path.join(base_dir, 'document', 'docker-cnn-google.json')
# json_filepath2 = os.path.join(base_dir, 'document', 'docker-cnn-2.json')

json_filepath = 'D:\môn học\lap_trinh_mang\CNN\docker-cnn\document\client_secret.json'
json_filepath1 = os.path.join(base_dir, 'document', 'docker-cnn-google.json')
json_filepath2 = 'D:\môn học\lap_trinh_mang\CNN\docker-cnn\document\docker-cnn-2.json '


print("---->>>>>json_filepath: ", json_filepath)
print("---->>>>>json_filepath1: ", json_filepath1)
print("---->>>>>json_filepath2: ", json_filepath2)


def save_credentials_to_json(credentials, filepath):
    scopes_list = list(credentials.scopes)

    credentials_info = {
        "access_token": credentials.access_token,
        "refresh_token": credentials.refresh_token,
        "token_expiry": credentials.token_expiry.isoformat(),
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "user_agent": credentials.user_agent,
        "token_response": credentials.token_response,
        "revoke_uri": credentials.revoke_uri,
        "scopes": scopes_list,  # Convert set to list
    }

    with open(filepath, 'w') as token_file:
        json.dump(credentials_info, token_file)


def upload_with_google_drive():
    gauth = GoogleAuth()
    gauth.auth_method = 'service'
    gauth.LoadClientConfigFile(json_filepath)
    gauth.LocalWebserverAuth()
    gauth.Authorize()
    print("gauth>>>>>>>>>>>>",gauth.credentials)
    save_credentials_to_json(gauth.credentials, 'D:/môn học/lap_trinh_mang/CNN/docker-cnn/document/token.json')
    return gauth

def load_credentials_from_json(filepath):
    with open(filepath, 'r') as token_file:
        credentials_info = json.load(token_file)
        return credentials_info

def set_credentials(gauth, credentials_info):
    gauth.access_token = credentials_info.get('access_token')
    gauth.refresh_token = credentials_info.get('refresh_token')
    gauth.token_expiry = datetime.fromisoformat(credentials_info.get('token_expiry'))
    gauth.client_id = credentials_info.get('client_id')
    gauth.client_secret = credentials_info.get('client_secret')
    gauth.user_agent = credentials_info.get('user_agent')
    gauth.token_response = credentials_info.get('token_response')
    gauth.revoke_uri = credentials_info.get('revoke_uri')
    gauth.scopes = credentials_info.get('scopes', [])

# def authenticate_with_google_drive():
#     gauth = GoogleAuth()
#     gauth.service_account_email = "updrive@docker-cnn.iam.gserviceaccount.com"
#     gauth.service_account_file = json_filepath2  # Đường dẫn đến tệp JSON của bạn
#     gauth.scope = ['https://www.googleapis.com/auth/drive']
#     gauth.GetAuth()
#     return gauth

# def authenticate_with_google_drive():
#     gauth = GoogleAuth()
#     gauth.service_account_email = 'updrive@docker-cnn.iam.gserviceaccount.com'
#     gauth.service_account_file = json_filepath2  # Thay đổi thành đường dẫn mới
#     gauth.scope = ['https://www.googleapis.com/auth/drive']
#     gauth.LocalWebserverAuth()
#     return gauth

def upload_to_drive():
    model_file_path = os.path.join('D:/môn học/lap_trinh_mang/CNN/docker-cnn/model/trained_new1.h5')
    try:
         # Load the credentials from the existing token
        credentials_info = load_credentials_from_json('D:/môn học/lap_trinh_mang/CNN/docker-cnn/document/token.json')

        # Initialize GoogleAuth
        gauth = GoogleAuth()

        # Set credentials
        set_credentials(gauth, credentials_info)

        # Authorize using the loaded credentials
        gauth.Authorize()

        drive = GoogleDrive(gauth)

        with open(model_file_path, "rb") as file_to_upload:
            

            # gauth = upload_with_google_drive()
            # drive = GoogleDrive(gauth)

           

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
        print("33333333333 >>> exception", e )
    finally:
        print("33333333333 >>> finally")
# alo nghe k?



# import os
# import tempfile
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive


# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')
# json_filepath1 = os.path.join(base_dir, 'document', 'docker-cnn-google.json')


# def authenticate_with_google_drive():
#     gauth = GoogleAuth()
#     gauth.auth_method = 'service'
#     gauth.LoadClientConfigFile(json_filepath1)
#     gauth.LocalWebserverAuth()
#     return gauth

# def upload_to_drive():
#     try:
#         model_file_path = 'D:/môn học/lap_trinh_mang/CNN/docker-cnn/model/trained_new1.h5'
#         gauth = authenticate_with_google_drive()
#         drive = GoogleDrive(gauth)

#         # Create a temporary zip file to upload to Google Drive
#         with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as temp_file:
#             temp_file.write(open(model_file_path, 'rb').read())

#             # Create a new file on Google Drive and set the content from the uploaded temp file
#             file_drive = drive.CreateFile({'title': 'trained_new1.h5'})
#             file_drive.SetContentFile(temp_file.name)
#             file_drive.Upload()

#             # Insert permission for anyone to read the file
#             file_drive.InsertPermission({
#                 'type': 'anyone',
#                 'value': 'anyone',
#                 'role': 'reader'
#             })

#             file_link = file_drive['alternateLink']
#             print("file_link  =>>>>>>>>>", file_link)
#     except Exception as e:
#         print("An error occurred:", str(e))

# if __name__ == "__main__":
#     upload_to_drive()