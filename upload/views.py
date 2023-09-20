import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')

def authenticate_google_drive(request):
    # Gọi API và nhận URL xác thực từ Google Drive
    # Ví dụ:
    authentication_url = "https://accounts.google.com/o/oauth2/auth..."  # URL xác thực thực sự từ Google Drive

    response_data = {
        'authentication_url': authentication_url
    }

    return JsonResponse(response_data)


def authenticate_with_google_drive(client_secrets_path):
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(client_secrets_path)
    gauth.LocalWebserverAuth()
    return gauth


def success(request):
    
    return render(request,'upload/upload_success.html')


def upload_folder(request):
    if request.method == 'POST':
        print("444444444")

        # Confirm Google Drive API
        file_to_upload = request.FILES.get('file')
        if not file_to_upload:
            return JsonResponse({'error': 'No file submitted.'}, status=400)

        if not file_to_upload.name.endswith('.zip'):
            return JsonResponse({'status': 'Only zip files are allowed.'}, status=400)

        print("33333333333")

        try:
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
                print("12222222222222222")

                file_link = file_drive['alternateLink']
                print("file_link  =>>>>>>>>>",file_link)

                return JsonResponse({
                    'success': 'upload success',
                    'url': file_link,
                    }, status=200)
                

        except Exception as e:
            print(e)
            # Handle exceptions appropriately, log the error, and provide a meaningful error message to the user
            return JsonResponse({'error': str(e)}, status=500)

        finally:
            print()

            # Ensure the temporary zip file is removed
            # if os.path.exists(temp_zip_file.name):
            #     os.unlink(temp_zip_file.name)

    return render(request, 'upload/upload.html')
