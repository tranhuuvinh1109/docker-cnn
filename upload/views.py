import os

from django.http import JsonResponse
from django.shortcuts import render
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')


def authenticate_with_google_drive(client_secrets_path):
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(client_secrets_path)
    gauth.LocalWebserverAuth()
    return gauth


# xu li up file zip
def upload_folder(request):
    if request.method == 'POST' and request.FILES['file']:
        # Xac nhan google drive api
        gauth = authenticate_with_google_drive(json_filepath)
        gauth.LocalWebserverAuth()

        # ket noi google
        drive = GoogleDrive(gauth)

        # up file
        file_to_upload = request.FILES['file']

        # kt la file zip
        if not file_to_upload.name.endswith('.zip'):
            return JsonResponse({'status': 'Only zip files are allowed.'}, status=400)

        # chuyen the binary
        file_content = file_to_upload.read()

        # Create a temporary zip file to upload to Google Drive
        temp_zip_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        temp_zip_file.write(file_content)
        temp_zip_file.close()

        try:
            # Create a new file on Google Drive and set the content from the uploaded zip file
            file_drive = drive.CreateFile({'title': file_to_upload.name})
            file_drive.SetContentFile(temp_zip_file.name)  # Set content from the temporary zip file
            file_drive.Upload()

            # tao link
            file_drive.InsertPermission({
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            })

            # lay link
            file_link = file_drive['alternateLink']
            print('Đây là liên kết chia sẻ tới file:', file_link)

            return JsonResponse({'status': file_link})
        finally:
            # Close and remove the temporary zip file
            os.unlink(temp_zip_file.name)

    return render(request, 'upload/upload.html')
